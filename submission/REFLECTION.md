# Reflection (Lab 19)

**1. Chế độ nào thắng ở loại câu hỏi nào và tại sao?**
- **Exact queries:** Keyword (BM25) chiếm ưu thế vì câu hỏi chứa chính xác các từ khóa kỹ thuật xuất hiện trong văn bản.
- **Paraphrase queries:** Semantic (Vector search) hoạt động tốt hơn do có khả năng hiểu ngữ nghĩa và gom cụm nội dung tương đồng, dù không trùng khớp từ khóa gốc.
- **Mixed queries:** Hybrid (RRF) thắng tuyệt đối. Các truy vấn thực tế thường pha trộn giữa từ khóa chính xác và ý diễn giải. Thuật toán RRF kết hợp phát huy trọn vẹn điểm mạnh của cả hai phương pháp trên.

**2. Khi nào không nên dùng Hybrid?**
Không nên dùng Hybrid search khi:
- Hệ thống có ngân sách thời gian cực thấp (đòi hỏi độ trễ ultra-low latency), vì Hybrid tốn kém tài nguyên để chạy cả 2 engine và tốn thêm thời gian tính toán RRF.
- Khi người dùng có chủ đích tìm kiếm chính xác mã ID, mã lỗi (error code) hoặc các thuật ngữ đặc thù mà BM25 đã xử lý hoàn hảo.

*(Ghi chú thêm: Trong quá trình test Notebook 3, do giới hạn sức mạnh tính toán của CPU laptop nên tốc độ API P99 server-side thấp nhất đạt ~137ms thay vì <50ms)*

**3. Tại sao agentic (+filter) lại có kết quả thấp hơn agentic (no filter)?**
Việc ép model tự động đoán và thêm điều kiện lọc (filter) làm giảm recall. Nguyên nhân là vì nếu đoán sai topic từ khóa, filter sẽ thẳng tay loại bỏ luôn những tài liệu liên quan nhưng nằm ở chủ đề lân cận. Bài học rút ra là: việc dùng filter mang lại rủi ro mất mát dữ liệu, cần phải đo đạc cẩn thận chứ không nên để AI tự đoán bừa.

**4. Lựa chọn ngưỡng tối ưu cho Semantic Cache và tại sao 0.75 là không đủ?**
- Ngưỡng tối ưu cho corpus này là **0.85**. Ở mức này, hệ thống vừa tiết kiệm được chi phí cao nhất mà vừa đưa tỷ lệ trả lời sai (false-hit) về 0%.
- Ngưỡng 0.75 (dù được AWS khuyến nghị chung) là không đủ an toàn trong trường hợp này, vì nó vẫn để lọt một tỷ lệ đáng kể các câu trả lời sai (false-hit), dẫn đến việc râu ông nọ cắm cằm bà kia.

**5. Bonus Challenge**
- Em đã hoàn thành phần Bonus Challenge (AI Memory). Toàn bộ mã nguồn, kịch bản test (POC) và tài liệu thiết kế hệ thống (kèm sơ đồ) được lưu trữ trong thư mục `bonus/`.
