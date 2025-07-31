// 导入必要的Java类库
package com.zhuermu;
import java.io.*;
import java.net.*;
import java.util.concurrent.CopyOnWriteArrayList;
import java.nio.charset.StandardCharsets; // 用于指定编码
import java.time.LocalDateTime; // 用于时间戳
import java.time.format.DateTimeFormatter; // 用于格式化时间戳

public class ChatServer {
    // 定义服务器端口号
    private static final int PORT = 12345;
    // 使用线程安全的列表保存所有客户端连接
    private static CopyOnWriteArrayList<ClientHandler> clients = new CopyOnWriteArrayList<>();
    // 时间戳格式
    private static final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    public static void main(String[] args) {
        System.out.println("Chat Server started...");

        // 使用try-with-resources自动管理ServerSocket资源
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            // 持续监听客户端连接
            while (true) {
                // 接受客户端连接（阻塞方法）
                Socket clientSocket = serverSocket.accept();
                System.out.println("New client connected: " + clientSocket);

                // 为每个客户端创建处理程序
                ClientHandler clientHandler = new ClientHandler(clientSocket);
                // 将客户端添加到列表
                clients.add(clientHandler);
                // 启动新线程处理该客户端
                new Thread(clientHandler).start();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // 内部类：客户端处理程序（实现Runnable接口）
    static class ClientHandler implements Runnable {
        private Socket socket;      // 客户端Socket对象
        private BufferedReader in;  // 输入流（接收客户端消息）
        private PrintWriter out;    // 输出流（向客户端发送消息）
        private String username;   // 客户端用户名

        public ClientHandler(Socket socket) {
            this.socket = socket;
            try {
                // 创建带有UTF-8编码的输入流
                in = new BufferedReader(new InputStreamReader(
                        socket.getInputStream(), StandardCharsets.UTF_8));
                // 创建带有UTF-8编码的输出流（自动刷新）
                out = new PrintWriter(new OutputStreamWriter(
                        socket.getOutputStream(), StandardCharsets.UTF_8), true);

                // 用户名获取流程
                out.println("ENTER_USERNAME"); // 发送获取用户名指令
                username = in.readLine();    // 读取客户端发来的用户名
                broadcast("\n"+getCurrentTimestamp() + " " + username + " has joined the chat room."); // 广播加入消息
            } catch (IOException e) {
                closeEverything(); // 发生异常时关闭资源
            }
        }

        @Override
        public void run() {
            try {
                String clientMessage;
                // 持续读取客户端消息
                while ((clientMessage = in.readLine()) != null) {
                    if (clientMessage.equalsIgnoreCase("exit")) {
                        break; // 客户端请求退出
                    }
                    broadcast(getCurrentTimestamp() + " " + username + " : " + clientMessage); // 广播消息
                }
            } catch (IOException e) {
                e.printStackTrace();
            } finally {
                closeEverything(); // 确保资源释放
                broadcast(getCurrentTimestamp() + " " + username + " has left the chat room."); // 广播离开消息
                clients.remove(this); // 从列表中移除
            }
        }

        // 广播消息给所有客户端（排除自己）
        private void broadcast(String message) {
            for (ClientHandler client : clients) {
                if (client != this) {
                    client.out.println(message); // 非阻塞式发送
                }
            }
        }

        // 安全关闭所有资源的方法
        private void closeEverything() {
            try {
                if (in != null) in.close();     // 关闭输入流
                if (out != null) out.close();     // 关闭输出流
                if (socket != null) socket.close(); // 关闭Socket
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        // 获取当前时间戳
        private String getCurrentTimestamp() {
            return LocalDateTime.now().format(formatter);
        }
    }
}