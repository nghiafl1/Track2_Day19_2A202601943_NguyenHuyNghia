# Kiến Trúc AI Memory: Episodic & Semantic Profile (POC)

## 1. Sơ đồ Kiến trúc Luồng Dữ liệu (Data Flow)

```mermaid
flowchart TD
    User([Người dùng]) -->|1. Input (Text)| Agent[Hybrid Memory Agent]
    
    subgraph Memory Modules
        Agent -->|2a. Phân tích Profile| FS[(Feature Store / Profile)]
        Agent -->|2b. Lưu Vector| VS[(Vector Store / Episodic)]
    end
    
    User -->|3. Query (Câu hỏi)| Agent
    Agent -->|4a. Lấy đặc trưng User| FS
    Agent -->|4b. Lấy ngữ cảnh tương đồng| VS
    FS -->|5. Trả về Preferences| ContextBuilder[Context Builder]
    VS -->|5. Trả về Top-K Memories| ContextBuilder
    ContextBuilder -->|6. Ngữ cảnh hoàn chỉnh| LLM[Large Language Model]
    LLM -->|7. Phản hồi cá nhân hoá| User
```

## 2. Các Quyết định Kiến trúc Cốt lõi và Trade-offs

### 2.1. Phân tách Episodic Memory và Profile (Feature Schema)
Thay vì lưu tất cả mọi câu nói của người dùng vào một không gian Vector duy nhất, hệ thống tách biệt rõ ràng giữa hai loại bộ nhớ:
- **Episodic Memory (Vector Store):** Lưu các sự kiện, hành động cụ thể xảy ra theo thời gian (ví dụ: "Sáng nay ăn bún chả").
- **Semantic Profile (Feature Store):** Lưu các đặc trưng, sở thích, thông tin tĩnh mang tính quy luật (ví dụ: "Thích phở bò", "Không ăn cay").
- **Trade-off:** Việc duy trì song song hai hệ thống làm tăng độ phức tạp của logic cập nhật (khi nào thì ghi vào Vector, khi nào ghi vào Feature Store). Tuy nhiên, đổi lại chi phí truy xuất giảm đáng kể. Bối cảnh (Context) cung cấp cho LLM sẽ luôn được đảm bảo chứa đựng sở thích nền tảng của người dùng mà không cần phải phụ thuộc hoàn toàn vào mức độ tương đồng vector (Vector Similarity) đầy rủi ro.

### 2.2. Chiến lược Cắt nhỏ Dữ liệu (Chunking Strategy cho ngữ cảnh Tiếng Việt)
- **Quyết định:** Sử dụng Sentence-based Chunking kết hợp với overlapping (gối đầu) thay vì Fixed-size Token Chunking. Đặc biệt, sử dụng thư viện chuyên dụng như `pyvi` hoặc `underthesea` để nhận diện ranh giới từ và câu trong tiếng Việt.
- **Trade-off:** Xử lý NLP tiếng Việt tốn thêm thời gian CPU, làm tăng latency lúc Ingestion so với việc cắt token thô sơ. Nhưng ưu điểm cực lớn là giữ được trọn vẹn ngữ nghĩa của câu tiếng Việt (vốn là ngôn ngữ đơn lập), tránh việc cắt vỡ một từ ghép (như "cân bằng / tải" bị cắt làm đôi) làm biến dạng vector nhúng của ngữ cảnh, gây nhiễu loạn bộ nhớ.

### 2.3. Chiến lược Làm mới (Freshness Strategy - Time Decay)
- **Quyết định:** Tích hợp `timestamp` vào Payload của Qdrant khi lưu Episodic Memory. Khi tiến hành Recall, điểm similarity gốc sẽ bị điều chỉnh trừ đi một lượng nhỏ (decay factor) dựa trên tuổi đời của dòng ký ức đó (những ký ức cũ cách đây 1 năm sẽ ít liên quan hơn ký ức vừa diễn ra hôm qua).
- **Trade-off:** Việc tính toán lại điểm số bằng Time Decay logic ở tầng ứng dụng làm tốn thêm một khoảng thời gian cực nhỏ trong việc xếp hạng (ranking). Tuy nhiên, nó giúp AI Agent cảm giác "giống con người" hơn bằng cách ưu tiên các sự kiện mới nhất, hạn chế việc mô hình bám vào một câu nói thay đổi sở thích từ 3 năm trước để trả lời cho bối cảnh hiện tại.

## 3. Lựa chọn Kiến trúc Đã Bị Loại Bỏ

**Bị loại bỏ: Graph Database (Knowledge Graph) cho AI Memory.**
- **Mô tả:** Ban đầu, ý tưởng là sử dụng Neo4j để lưu các mối quan hệ logic (ví dụ: `[Người dùng] -THÍCH-> [Phở]`).
- **Lý do loại bỏ:** Mặc dù Graph Database cho khả năng suy luận logic tuyệt vời, nhưng việc trích xuất các mối quan hệ (triplets) từ câu nói tự nhiên tiếng Việt không có cấu trúc là cực kỳ tốn kém và thiếu chính xác nếu dùng mô hình NLP truyền thống, hoặc tốn quá nhiều tiền API nếu gọi LLM để trích xuất liên tục. Đối với POC này, một tổ hợp giữa Vector Store (Qdrant) và Key-Value Feature Store là quá đủ để tạo ra bối cảnh cá nhân hóa (hyper-personalization) mạnh mẽ mà độ trễ (latency) chỉ dưới 20ms, đồng thời tiết kiệm hơn 90% chi phí phát triển và vận hành so với Knowledge Graph.
