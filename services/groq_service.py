import csv
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "subject_list.csv")
ROADMAP_CSV_PATH = os.path.join(BASE_DIR, "data", "roadmap_list.csv")
ROADMAP_SUBJECT_PATH = os.path.join(BASE_DIR, "data", "roadmap_subject.csv")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def load_csv(path):
    """Load CSV file and return list of dictionaries"""
    try:
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception as e:
        print(f"Error loading CSV {path}: {e}")
        return []


def get_csv_context():
    """Get all CSV data to send to Groq"""
    subjects = load_csv(CSV_PATH)
    roadmaps = load_csv(ROADMAP_CSV_PATH)
    roadmap_subjects = load_csv(ROADMAP_SUBJECT_PATH)
    
    # Format subjects data
    subjects_text = "Danh sách các khóa học:\n"
    for s in subjects:
        subjects_text += f"- {s['subject_name']} (Ngành: {s['category']}, Mức độ: {s['level']}, Giờ học: {s['study_hours']}, Mô tả: {s['description']})\n"
    
    # Format roadmaps data
    roadmaps_text = "\nDanh sách các lộ trình học tập:\n"
    for r in roadmaps:
        roadmaps_text += f"- {r['roadmap_name']} (Ngành: {r['career_group']}, Mô tả: {r['description']})\n"
    
    return subjects_text + roadmaps_text


def get_ai_recommendation(user_info):
    """
    Get personalized learning roadmap recommendation from Groq
    
    Args:
        user_info: dict with keys:
            - year: int (1-4)
            - gpa: float
            - hours_per_week: int
            - career_goal: str
            - learning_mode: str (online/offline/hybrid)
            - resource: str (video/book/practice) - optional
            - level: str (beginner/intermediate/advanced)
            - custom_goal: str - optional
    
    Returns:
        str: Markdown-formatted recommendation from Groq
    """
    try:
        # Get CSV context
        csv_context = get_csv_context()
        
        # Prepare user context
        career_goal = user_info.get('custom_goal') or user_info.get('career_goal')
        learning_mode = user_info.get('learning_mode', 'không xác định')
        resource_pref = user_info.get('resource', 'không xác định')
        
        user_context = f"""
Thông tin sinh viên:
- Năm học: {user_info.get('year', 'N/A')}
- GPA hiện tại: {user_info.get('gpa', 'N/A')}
- Giờ học mỗi tuần: {user_info.get('hours_per_week', 'N/A')} giờ
- Mục tiêu nghề nghiệp: {career_goal}
- Hình thức học: {learning_mode}
- Nguồn học tập ưu tiên: {resource_pref}
- Mức độ hiện tại: {user_info.get('level', 'cơ bản')}
"""
        
        # Create prompt for Groq
        prompt = f"""{csv_context}

{user_context}

Dựa trên thông tin sinh viên và danh sách các khóa học, lộ trình, hãy:
1. Phân tích nhu cầu học tập của sinh viên
2. Đề xuất 1 lộ trình học tập chi tiết (nếu có trong danh sách, hoặc tạo mới dựa trên các khóa học có sẵn)
3. Liệt kê 5-7 khóa học cụ thể được đề xuất theo thứ tự ưu tiên
4. Cung cấp lời khuyên về thời gian biểu và chiến lược học tập

Lưu ý: 
- Hãy xem xét GPA, năm học và giờ học mỗi tuần để đưa ra khuyến cáo phù hợp
- Ưu tiên các khóa học phù hợp với hình thức học ({learning_mode}) và nguồn tài nguyên ({resource_pref})
- Đảm bảo lộ trình có thể hoàn thành trong năm học hiện tại
- Trả lời bằng tiếng Việt
- **Format đáp án bằng Markdown** với các tiêu đề rõ ràng (dùng ##, ###), danh sách (dùng -), và **đậm** để làm nổi bật các phần quan trọng
- Cấu trúc câu trả lời dễ đọc với các phần tiêu đề (## Tiêu đề), danh sách điểm, và giải thích chi tiết"""
        
        # Call Groq API
        message = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.choices[0].message.content
        
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return f"<div class='alert alert-danger'>Lỗi khi tạo đề xuất: {str(e)}</div>"


def chat_about_roadmap(user_question, current_recommendation, user_info, conversation_history=None):
    """
    Chat with AI about the recommended roadmap
    
    Args:
        user_question: str - User's question
        current_recommendation: str - The previously generated recommendation
        user_info: dict - User information
        conversation_history: list - Previous messages with role and content keys
    
    Returns:
        str: AI response about the roadmap
    """
    try:
        # Get CSV context for reference
        csv_context = get_csv_context()
        
        # Build system message with context
        system_message = f"""{csv_context}

Bạn là trợ lý học tập AI chuyên tư vấn lộ trình học tập cho sinh viên.
Người dùng đã nhận được đề xuất lộ trình này:

{current_recommendation}

Hãy trả lời các câu hỏi của sinh viên về lộ trình, các khóa học, thời gian học, v.v.
**Format câu trả lời bằng Markdown rõ ràng**: dùng ## hoặc ### cho tiêu đề, dùng - cho danh sách điểm, **đậm** cho phần quan trọng.
Trả lời bằng tiếng Việt, ngắn gọn và rõ ràng."""

        # Prepare messages - include system message as first message
        messages = [
            {"role": "user", "content": system_message},
            {"role": "assistant", "content": "Tôi đã hiểu. Tôi sẽ giúp bạn trả lời các câu hỏi về lộ trình học tập này."}
        ]
        
        # Add conversation history if exists
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current question
        messages.append({"role": "user", "content": user_question})
        
        # Call Groq API
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1024,
            messages=messages
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error in chat: {e}")
        return f"Lỗi: {str(e)}"


def chat_directly(user_question):
    """
    Direct chat about courses and roadmaps without user profile
    
    Args:
        user_question: str - User's question about courses/roadmaps
    
    Returns:
        str: AI response about the available courses
    """
    try:
        # Get CSV context
        csv_context = get_csv_context()
        
        # System message for direct chat
        system_message = f"""{csv_context}

Bạn là trợ lý học tập AI chuyên tư vấn về các khóa học và lộ trình học tập.
Hãy trả lời các câu hỏi của người dùng về:
- Các khóa học có sẵn
- Lộ trình học tập
- Yêu cầu tiên quyết
- Thời gian học
- Nội dung khóa học
- Lợi ích của mỗi khóa học

**Format câu trả lời bằng Markdown rõ ràng**: dùng ## hoặc ### cho tiêu đề, dùng - cho danh sách điểm, **đậm** cho phần quan trọng.
Trả lời bằng tiếng Việt, ngắn gọn và rõ ràng. Tham khảo danh sách khóa học và lộ trình phía trên."""

        # Build messages with system as first user message
        messages = [
            {"role": "user", "content": system_message},
            {"role": "assistant", "content": "Tôi đã hiểu. Tôi sẽ giúp bạn tìm hiểu về các khóa học và lộ trình học tập."},
            {"role": "user", "content": user_question}
        ]
        
        # Call Groq API
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1024,
            messages=messages
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error in direct chat: {e}")
        return f"Lỗi: {str(e)}"