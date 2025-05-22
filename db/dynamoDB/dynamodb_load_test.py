#!/usr/bin/env python3
"""
DynamoDB 压力测试脚本
模拟多用户并发读写广告点击数据到 DynamoDB 表中
支持 TPS (Transactions Per Second) 控制
"""

import boto3
import time
import uuid
import random
import threading
import argparse
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from botocore.exceptions import ClientError

# 配置参数
DEFAULT_REGION = 'us-east-1'
DEFAULT_TABLE = 'first_dyn_table_new'
DEFAULT_WRITE_THREADS = 10
DEFAULT_READ_THREADS = 5
DEFAULT_WRITE_DURATION_MINUTES = 5
DEFAULT_READ_DURATION_MINUTES = 5
DEFAULT_BATCH_SIZE = 25  # 每个线程每批次写入的项目数
DEFAULT_WRITE_TPS = 0    # 默认不限制 TPS (0 表示不限制)
DEFAULT_READ_TPS = 0     # 默认不限制 TPS (0 表示不限制)

# 广告类型列表
AD_TYPES = ['banner', 'video', 'popup', 'interstitial', 'native']

# 广告位置列表
AD_POSITIONS = ['top', 'bottom', 'sidebar', 'in-feed', 'in-article']

# 渠道来源列表
CHANNELS = ['facebook', 'google', 'twitter', 'instagram', 'tiktok', 
            'direct', 'email', 'partner', 'affiliate', 'organic']

# 生成随机URL的域名列表
DOMAINS = ['example.com', 'adservice.com', 'clicktrack.net', 'adnetwork.org', 'mediaads.co']

# 生成随机URL的路径列表
PATHS = ['/product/', '/campaign/', '/offer/', '/promo/', '/special/', '/deal/']

class TPSController:
    """TPS (Transactions Per Second) 控制器"""
    def __init__(self, target_tps):
        """
        初始化 TPS 控制器
        
        参数:
            target_tps: 目标 TPS，0 表示不限制
        """
        self.target_tps = target_tps
        self.lock = threading.Lock()
        self.last_second = int(time.time())
        self.transactions_this_second = 0
        self.enabled = target_tps > 0
    
    def wait_for_next_transaction(self):
        """等待下一个事务的执行时间"""
        if not self.enabled:
            return
        
        with self.lock:
            current_second = int(time.time())
            
            # 如果进入了新的一秒，重置计数器
            if current_second > self.last_second:
                self.last_second = current_second
                self.transactions_this_second = 0
            
            # 如果当前秒内的事务数已达到目标 TPS，则等待下一秒
            if self.transactions_this_second >= self.target_tps:
                sleep_time = 1.0 - (time.time() - current_second)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                # 重置为新的一秒
                self.last_second = int(time.time())
                self.transactions_this_second = 0
            
            # 增加事务计数
            self.transactions_this_second += 1

class DynamoDBLoadTest:
    def __init__(self, table_name, region, write_threads, read_threads, 
                 write_duration_minutes, read_duration_minutes, batch_size,
                 write_tps, read_tps):
        self.table_name = table_name
        self.region = region
        self.write_threads = write_threads
        self.read_threads = read_threads
        self.write_duration_minutes = write_duration_minutes
        self.read_duration_minutes = read_duration_minutes
        self.batch_size = batch_size
        
        # 初始化 TPS 控制器
        self.write_tps_controller = TPSController(write_tps)
        self.read_tps_controller = TPSController(read_tps)
        
        # 计算每个线程的 TPS 分配
        self.write_tps_per_thread = write_tps / write_threads if write_threads > 0 and write_tps > 0 else 0
        self.read_tps_per_thread = read_tps / read_threads if read_threads > 0 and read_tps > 0 else 0
        
        # 初始化 DynamoDB 客户端和资源
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.dynamodb_client = boto3.client('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
        
        # 控制线程停止的事件
        self.write_stop_event = threading.Event()
        self.read_stop_event = threading.Event()
        
        # 统计信息 - 项目数
        self.total_items_written = 0
        self.total_items_read = 0
        
        # 统计信息 - 事务数
        self.total_write_transactions = 0
        self.total_read_transactions = 0
        
        # 错误计数
        self.write_errors = 0
        self.read_errors = 0
        
        # 线程安全锁
        self.write_lock = threading.Lock()
        self.read_lock = threading.Lock()
        
        # 记录开始时间
        self.write_start_time = None
        self.read_start_time = None
        
        # 用于存储写入的用户ID，以便读取线程使用
        self.user_ids = list(range(1, write_threads + 1))
        
        # TPS 监控
        self.write_tps_history = []
        self.read_tps_history = []
        self.tps_monitor_interval = 5  # 每5秒记录一次 TPS

    def generate_ad_data(self, user_id):
        """生成模拟的广告点击数据"""
        # 使用微秒级时间戳，确保唯一性
        timestamp = int(time.time() * 1000000)
        # 添加一个小的随机偏移，进一步确保唯一性
        timestamp += random.randint(1, 999999)
        
        click_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        ad_id = f"ad-{uuid.uuid4().hex[:8]}"
        ad_type = random.choice(AD_TYPES)
        ad_position = random.choice(AD_POSITIONS)
        channel = random.choice(CHANNELS)
        click_id = f"click-{uuid.uuid4().hex}"
        domain = random.choice(DOMAINS)
        path = random.choice(PATHS) + uuid.uuid4().hex[:8]
        url = f"https://{domain}{path}"
        
        # 生成随机的额外数据，确保总大小约为2KB
        extra_data = {
            f"field_{i}": uuid.uuid4().hex for i in range(45)
        }
        
        # 构建完整的项目数据
        item = {
            'userid': user_id,
            'timestamp': timestamp,
            'click_time': click_time,
            'ad_id': ad_id,
            'ad_type': ad_type,
            'ad_position': ad_position,
            'channel': channel,
            'click_id': click_id,
            'click_url': url,
            'extra_data': json.dumps(extra_data)
        }
        
        return item

    def write_worker(self, thread_id):
        """写入工作线程函数，持续写入数据直到达到指定时间"""
        user_id = thread_id + 1  # 使用线程ID作为用户ID
        items_written = 0
        transactions = 0
        batch_count = 0
        
        # 创建线程级别的 TPS 控制器
        tps_controller = TPSController(self.write_tps_per_thread) if self.write_tps_per_thread > 0 else None
        
        print(f"Write Thread {thread_id} started (User ID: {user_id})")
        
        while not self.write_stop_event.is_set():
            try:
                # 如果使用全局 TPS 控制，等待下一个事务时间窗口
                if self.write_tps_controller.enabled:
                    self.write_tps_controller.wait_for_next_transaction()
                # 如果使用线程级 TPS 控制，等待下一个事务时间窗口
                elif tps_controller and tps_controller.enabled:
                    tps_controller.wait_for_next_transaction()
                
                # 批量写入数据
                with self.table.batch_writer() as batch:
                    for _ in range(self.batch_size):
                        # 为每个项目生成唯一的数据
                        item = self.generate_ad_data(user_id)
                        batch.put_item(Item=item)
                        items_written += 1
                        # 添加小延迟，确保时间戳不同
                        time.sleep(0.001)
                
                # 每个批量写入算作一个事务
                transactions += 1
                batch_count += 1
                
                # 每10批次输出一次状态
                if batch_count % 10 == 0:
                    elapsed = time.time() - self.write_start_time
                    print(f"Write Thread {thread_id}: Written {items_written} items in {elapsed:.2f} seconds")
                
                # 短暂休眠，避免过度消耗CPU
                time.sleep(0.01)
                
            except ClientError as e:
                print(f"Error in write thread {thread_id}: {e}")
                with self.write_lock:
                    self.write_errors += 1
                time.sleep(1)  # 出错后稍微等待一下
        
        # 更新总写入计数
        with self.write_lock:
            self.total_items_written += items_written
            self.total_write_transactions += transactions
        
        print(f"Write Thread {thread_id} finished. Items written: {items_written}, Transactions: {transactions}")

    def read_worker(self, thread_id):
        """读取工作线程函数，持续读取数据直到达到指定时间"""
        items_read = 0
        transactions = 0
        query_count = 0
        
        # 创建线程级别的 TPS 控制器
        tps_controller = TPSController(self.read_tps_per_thread) if self.read_tps_per_thread > 0 else None
        
        print(f"Read Thread {thread_id} started")
        
        while not self.read_stop_event.is_set():
            try:
                # 如果使用全局 TPS 控制，等待下一个事务时间窗口
                if self.read_tps_controller.enabled:
                    self.read_tps_controller.wait_for_next_transaction()
                # 如果使用线程级 TPS 控制，等待下一个事务时间窗口
                elif tps_controller and tps_controller.enabled:
                    tps_controller.wait_for_next_transaction()
                
                # 随机选择一个用户ID进行查询
                user_id = random.choice(self.user_ids)
                
                # 查询最近的N条记录
                limit = random.randint(10, 50)
                
                # 执行查询
                response = self.table.query(
                    KeyConditionExpression=boto3.dynamodb.conditions.Key('userid').eq(user_id),
                    Limit=limit,
                    ScanIndexForward=False  # 降序排列，获取最新的记录
                )
                
                # 统计读取的项目数
                items_count = len(response.get('Items', []))
                items_read += items_count
                
                # 每次查询算作一个事务
                transactions += 1
                query_count += 1
                
                # 每10次查询输出一次状态
                if query_count % 10 == 0:
                    elapsed = time.time() - self.read_start_time
                    print(f"Read Thread {thread_id}: Read {items_read} items in {elapsed:.2f} seconds")
                
                # 短暂休眠，避免过度消耗CPU
                # time.sleep(0.05)
                
            except ClientError as e:
                print(f"Error in read thread {thread_id}: {e}")
                with self.read_lock:
                    self.read_errors += 1
                time.sleep(1)  # 出错后稍微等待一下
        
        # 更新总读取计数
        with self.read_lock:
            self.total_items_read += items_read
            self.total_read_transactions += transactions
        
        print(f"Read Thread {thread_id} finished. Items read: {items_read}, Transactions: {transactions}")

    def monitor_tps(self, operation_type):
        """监控 TPS 的线程函数"""
        last_items = 0
        last_transactions = 0
        start_time = time.time()
        
        while True:
            time.sleep(self.tps_monitor_interval)
            
            if operation_type == 'write':
                if self.write_stop_event.is_set():
                    break
                current_items = self.total_items_written
                current_transactions = self.total_write_transactions
                history = self.write_tps_history
            else:  # read
                if self.read_stop_event.is_set():
                    break
                current_items = self.total_items_read
                current_transactions = self.total_read_transactions
                history = self.read_tps_history
            
            # 计算这个时间间隔内的 TPS 和吞吐量
            interval_items = current_items - last_items
            interval_transactions = current_transactions - last_transactions
            
            items_per_second = interval_items / self.tps_monitor_interval
            tps = interval_transactions / self.tps_monitor_interval
            
            # 记录 TPS 历史
            elapsed = time.time() - start_time
            history.append((elapsed, tps))
            
            # 输出当前 TPS 和吞吐量
            print(f"Current {operation_type.capitalize()} - TPS: {tps:.2f} transactions/second, Throughput: {items_per_second:.2f} items/second")
            
            last_items = current_items
            last_transactions = current_transactions

    def run_write_test(self):
        """运行写入负载测试"""
        print(f"\n--- Starting Write Load Test ---")
        print(f"Threads: {self.write_threads}")
        print(f"Duration: {self.write_duration_minutes} minutes")
        print(f"Batch size: {self.batch_size}")
        print(f"Target Write TPS: {'Unlimited' if self.write_tps_controller.target_tps == 0 else self.write_tps_controller.target_tps}")
        
        # 记录开始时间
        self.write_start_time = time.time()
        write_end_time = self.write_start_time + (self.write_duration_minutes * 60)
        
        # 启动 TPS 监控线程
        tps_monitor_thread = threading.Thread(target=self.monitor_tps, args=('write',))
        tps_monitor_thread.daemon = True
        tps_monitor_thread.start()
        
        # 创建并启动写入工作线程
        with ThreadPoolExecutor(max_workers=self.write_threads) as executor:
            write_futures = [executor.submit(self.write_worker, i) for i in range(self.write_threads)]
            
            # 等待指定的持续时间
            try:
                while time.time() < write_end_time:
                    elapsed = time.time() - self.write_start_time
                    remaining = write_end_time - time.time()
                    print(f"Write test running for {elapsed:.2f} seconds. {remaining:.2f} seconds remaining.")
                    time.sleep(10)  # 每10秒更新一次状态
            except KeyboardInterrupt:
                print("Write test interrupted by user.")
            finally:
                # 通知所有写入线程停止
                self.write_stop_event.set()
                print("Waiting for write threads to finish...")
                
                # 等待所有写入线程完成
                for future in write_futures:
                    future.result()
        
        # 计算并显示写入结果
        total_write_time = time.time() - self.write_start_time
        items_per_second = self.total_items_written / total_write_time if total_write_time > 0 else 0
        transactions_per_second = self.total_write_transactions / total_write_time if total_write_time > 0 else 0
        
        print("\n--- Write Test Results ---")
        print(f"Total items written: {self.total_items_written}")
        print(f"Total write transactions: {self.total_write_transactions}")
        print(f"Total time: {total_write_time:.2f} seconds")
        print(f"Average write throughput: {items_per_second:.2f} items/second")
        print(f"Average write TPS: {transactions_per_second:.2f} transactions/second")
        print(f"Write errors encountered: {self.write_errors}")
        
        # 显示 TPS 统计
        if self.write_tps_history:
            tps_values = [tps for _, tps in self.write_tps_history]
            avg_tps = sum(tps_values) / len(tps_values)
            max_tps = max(tps_values)
            min_tps = min(tps_values)
            print(f"TPS Statistics - Avg: {avg_tps:.2f}, Max: {max_tps:.2f}, Min: {min_tps:.2f}")

    def run_read_test(self):
        """运行读取负载测试"""
        print(f"\n--- Starting Read Load Test ---")
        print(f"Threads: {self.read_threads}")
        print(f"Duration: {self.read_duration_minutes} minutes")
        print(f"Target Read TPS: {'Unlimited' if self.read_tps_controller.target_tps == 0 else self.read_tps_controller.target_tps}")
        
        # 记录开始时间
        self.read_start_time = time.time()
        read_end_time = self.read_start_time + (self.read_duration_minutes * 60)
        
        # 启动 TPS 监控线程
        tps_monitor_thread = threading.Thread(target=self.monitor_tps, args=('read',))
        tps_monitor_thread.daemon = True
        tps_monitor_thread.start()
        
        # 创建并启动读取工作线程
        with ThreadPoolExecutor(max_workers=self.read_threads) as executor:
            read_futures = [executor.submit(self.read_worker, i) for i in range(self.read_threads)]
            
            # 等待指定的持续时间
            try:
                while time.time() < read_end_time:
                    elapsed = time.time() - self.read_start_time
                    remaining = read_end_time - time.time()
                    print(f"Read test running for {elapsed:.2f} seconds. {remaining:.2f} seconds remaining.")
                    time.sleep(10)  # 每10秒更新一次状态
            except KeyboardInterrupt:
                print("Read test interrupted by user.")
            finally:
                # 通知所有读取线程停止
                self.read_stop_event.set()
                print("Waiting for read threads to finish...")
                
                # 等待所有读取线程完成
                for future in read_futures:
                    future.result()
        
        # 计算并显示读取结果
        total_read_time = time.time() - self.read_start_time
        items_per_second = self.total_items_read / total_read_time if total_read_time > 0 else 0
        transactions_per_second = self.total_read_transactions / total_read_time if total_read_time > 0 else 0
        
        print("\n--- Read Test Results ---")
        print(f"Total items read: {self.total_items_read}")
        print(f"Total read transactions (queries): {self.total_read_transactions}")
        print(f"Total time: {total_read_time:.2f} seconds")
        print(f"Average read throughput: {items_per_second:.2f} items/second")
        print(f"Average read TPS: {transactions_per_second:.2f} transactions/second")
        print(f"Read errors encountered: {self.read_errors}")
        
        # 显示 TPS 统计
        if self.read_tps_history:
            tps_values = [tps for _, tps in self.read_tps_history]
            avg_tps = sum(tps_values) / len(tps_values)
            max_tps = max(tps_values)
            min_tps = min(tps_values)
            print(f"TPS Statistics - Avg: {avg_tps:.2f}, Max: {max_tps:.2f}, Min: {min_tps:.2f}")

    def run(self):
        """运行完整的负载测试（写入和读取）"""
        print(f"Starting DynamoDB load test on table '{self.table_name}'")
        print(f"Region: {self.region}")
        
        # 运行写入测试
        self.run_write_test()
        
        # 运行读取测试
        self.run_read_test()
        
        print("\n--- Overall Test Complete ---")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='DynamoDB Load Test')
    parser.add_argument('--table', type=str, default=DEFAULT_TABLE,
                        help=f'DynamoDB table name (default: {DEFAULT_TABLE})')
    parser.add_argument('--region', type=str, default=DEFAULT_REGION,
                        help=f'AWS region (default: {DEFAULT_REGION})')
    parser.add_argument('--write-threads', type=int, default=DEFAULT_WRITE_THREADS,
                        help=f'Number of concurrent write threads (default: {DEFAULT_WRITE_THREADS})')
    parser.add_argument('--read-threads', type=int, default=DEFAULT_READ_THREADS,
                        help=f'Number of concurrent read threads (default: {DEFAULT_READ_THREADS})')
    parser.add_argument('--write-duration', type=int, default=DEFAULT_WRITE_DURATION_MINUTES,
                        help=f'Write test duration in minutes (default: {DEFAULT_WRITE_DURATION_MINUTES})')
    parser.add_argument('--read-duration', type=int, default=DEFAULT_READ_DURATION_MINUTES,
                        help=f'Read test duration in minutes (default: {DEFAULT_READ_DURATION_MINUTES})')
    parser.add_argument('--batch-size', type=int, default=DEFAULT_BATCH_SIZE,
                        help=f'Items per batch write (default: {DEFAULT_BATCH_SIZE})')
    parser.add_argument('--write-tps', type=int, default=DEFAULT_WRITE_TPS,
                        help=f'Target write transactions per second, 0 for unlimited (default: {DEFAULT_WRITE_TPS})')
    parser.add_argument('--read-tps', type=int, default=DEFAULT_READ_TPS,
                        help=f'Target read transactions per second, 0 for unlimited (default: {DEFAULT_READ_TPS})')
    parser.add_argument('--write-only', action='store_true',
                        help='Run only the write test')
    parser.add_argument('--read-only', action='store_true',
                        help='Run only the read test')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    
    # 创建负载测试实例
    load_test = DynamoDBLoadTest(
        table_name=args.table,
        region=args.region,
        write_threads=args.write_threads,
        read_threads=args.read_threads,
        write_duration_minutes=args.write_duration,
        read_duration_minutes=args.read_duration,
        batch_size=args.batch_size,
        write_tps=args.write_tps,
        read_tps=args.read_tps
    )
    
    # 根据参数决定运行哪些测试
    if args.write_only:
        load_test.run_write_test()
    elif args.read_only:
        load_test.run_read_test()
    else:
        load_test.run()
