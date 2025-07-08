import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.Scanner;
import java.time.LocalDateTime; // 用于时间戳
import java.time.format.DateTimeFormatter; // 用于格式化时间戳

public class ChatClient {
    // 服务器配置
    private static final String SERVER_IP = "localhost";
    private static final int SERVER_PORT = 12345;
    // 线程共享标志位（volatile保证可见性）
    private static volatile boolean needUsername = false;
    // 时间戳格式
    private static final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    public static void main(String[] args) {
        // 使用try-with-resources自动管理Socket连接
        try (Socket socket = new Socket(SERVER_IP, SERVER_PORT)) {
            // 创建带编码的输入输出流
            Scanner serverScanner = new Scanner(socket.getInputStream(), StandardCharsets.UTF_8.name());
            PrintWriter out = new PrintWriter(new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8), true);

            // 使用UTF-8编码的Scanner读取控制台输入
            Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8.name());

            // 消息接收线程（仅显示消息）
            new Thread(() -> {
                try {
                    while (serverScanner.hasNextLine()) {
                        String serverMessage = serverScanner.nextLine();
                        if ("ENTER_USERNAME".equals(serverMessage)) {
                            needUsername = true; // 设置用户名输入标志
                        } else {
                            System.out.println(serverMessage); // 显示常规消息
                        }
                    }
                } catch (Exception e) {
                    System.out.println("[System] Connection to the server has been lost.");
                }
            }).start(); // 启动线程
            System.out.println("Welcome to the Chat Room!");

            // 主线程处理所有输入操作
            while (true) {

                if (needUsername) {
                    System.out.print("Please enter your username: ");
                    // 先输出提示信息
                    String username = scanner.nextLine(); // 然后等待用户输入用户名

                    if (username.trim().isEmpty()) { // 检查用户名是否为空
                        System.out.println("Username cannot be empty. Please try again.");
                        continue; // 如果用户名为空，提示用户重新输入
                    }
                    out.println(username); // 发送用户名到服务器
                    needUsername = false;   // 重置标志
                    continue; // 跳过本次循环剩余代码
                }

                // 处理常规消息输入
                String input = scanner.nextLine();
                if ("exit".equalsIgnoreCase(input)) {
                    out.println("exit"); // 发送退出指令
                    break; // 退出循环
                }
                out.println(input); // 发送普通消息
            }

        } catch (IOException e) {
            System.out.println("Unable to connect to the server");
        }
    }
}