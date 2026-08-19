from agent import HybridMemoryAgent

def main():
    agent = HybridMemoryAgent()
    user = "u_vn_001"
    
    print("========================================")
    print("1. Đang nạp dữ liệu vào AI Memory...")
    print("========================================")
    
    memories = [
        "Tôi tên là Nghĩa và tôi đang sống ở Hà Nội.",
        "Tôi rất thích ăn phở bò.",
        "Sáng nay tôi vừa đi ăn bún chả.",
        "Tôi không thích đồ ăn quá cay.",
        "Dự án AI của tôi đang dùng FastAPI và Qdrant."
    ]
    
    for m in memories:
        agent.remember(m, user)
        print(f" [+] Đã nhớ: {m}")
        
    queries = [
        "Tôi tên là gì và sống ở đâu?",
        "Sáng nay tôi ăn gì?",
        "Món ăn yêu thích của tôi là gì?",
        "Dự án của tôi dùng công nghệ gì?",
        "Bạn có gợi ý món nào cho tôi ăn trưa không?"
    ]
    
    print("\n========================================")
    print("2. Recall (Trích xuất) ngữ cảnh cho 5 câu hỏi đa dạng")
    print("========================================")
    for i, q in enumerate(queries, 1):
        print(f"\n[Câu hỏi {i}]: {q}")
        context = agent.recall(q, user)
        
        print("  [Hồ sơ tĩnh (Profile / Feature Store)]:")
        for pref in context["user_profile"]:
            print(f"      - {pref}")
            
        print("  [Ký ức sự kiện (Episodic / Vector Store)]:")
        if not context["relevant_episodes"]:
            print("      - Không tìm thấy ký ức liên quan.")
        else:
            for ep in context["relevant_episodes"]:
                print(f"      - {ep}")

if __name__ == "__main__":
    main()
