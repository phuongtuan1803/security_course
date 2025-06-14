#!/bin/bash

# QUAN TRỌNG: Thay địa chỉ IP của PC2 vào đây
SERVER_IP="192.168.195.159"
PORT=9999
COUNT=1

echo "Bắt đầu gửi gói tin liên tục đến $SERVER_IP:$PORT..."
echo "Nhấn Ctrl+C để dừng."
echo "---------------------------------------------"

# Vòng lặp vô hạn để gửi gói tin
while true; do
  # Tạo nội dung gói tin bao gồm số thứ tự và thời gian hiện tại
  MESSAGE="Package no $COUNT | Time: $(date)"

  # In ra màn hình để biết đã gửi
  echo "Sending: $MESSAGE"

  # Gửi gói tin bằng nc
  echo "$MESSAGE" | nc $SERVER_IP $PORT

  # Tăng biến đếm
  COUNT=$((COUNT + 1))

  # Chờ 1 giây trước khi gửi gói tin tiếp theo
  sleep 1
done