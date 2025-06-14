#!/bin/bash

PORT=9999

echo "Server đang lắng nghe trên cổng $PORT..."
echo "-------------------------------------"

# Vòng lặp vô hạn để liên tục lắng nghe kết nối mới
while true; do
  # nc sẽ lắng nghe, in ra dữ liệu nhận được, rồi kết thúc
  # Vòng lặp while sẽ chạy lại nc để chờ kết nối tiếp theo
  nc -l -w 1 -p $PORT
done