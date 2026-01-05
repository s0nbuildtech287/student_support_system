"""
Groq AI Service for Study Recommendation
"""
import os
import csv
import requests
from config import Config

class GroqService:
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    @staticmethod
    def get_api_key():
        return os.getenv('GROQ_API_KEY', '')
    
    @staticmethod
    def load_csv_data():
        """Load all CSV data from data folder"""
        data_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        
        # Load subjects
        subjects = []
        subject_file = os.path.join(data_folder, 'subject_list.csv')
        if os.path.exists(subject_file):
            with open(subject_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                subjects = list(reader)
        
        # Load roadmaps
        roadmaps = []
        roadmap_file = os.path.join(data_folder, 'roadmap_list.csv')
        if os.path.exists(roadmap_file):
            with open(roadmap_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                roadmaps = list(reader)
        
        # Load roadmap-subject mapping
        roadmap_subjects = []
        mapping_file = os.path.join(data_folder, 'roadmap_subject.csv')
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                roadmap_subjects = list(reader)
        
        return subjects, roadmaps, roadmap_subjects
    
    @staticmethod
    def build_context():
        """Build context from CSV data for AI"""
        subjects, roadmaps, roadmap_subjects = GroqService.load_csv_data()
        
        # Build subject info
        subject_info = "📚 DANH SÁCH MÔN HỌC:\n"
        for s in subjects:
            subject_info += f"- ID {s.get('id')}: {s.get('subject_name')} | Level: {s.get('level')} | Career: {s.get('career_group')} | Hours: {s.get('study_hours')}h | Desc: {s.get('description')}\n"
        
        # Build roadmap info
        roadmap_info = "\n🗺️ DANH SÁCH LỘ TRÌNH:\n"
        for r in roadmaps:
            roadmap_info += f"- ID {r.get('roadmap_id')}: {r.get('roadmap_name')} | Career: {r.get('career_group')} | Level: {r.get('level')} | Desc: {r.get('description')}\n"
        
        # Build roadmap-subject mapping
        mapping_info = "\n🔗 MÔN HỌC TRONG TỪNG LỘ TRÌNH:\n"
        current_roadmap = None
        for m in roadmap_subjects:
            rid = m.get('roadmap_id')
            if rid != current_roadmap:
                current_roadmap = rid
                # Find roadmap name
                rname = next((r.get('roadmap_name') for r in roadmaps if r.get('roadmap_id') == rid), f"Roadmap {rid}")
                mapping_info += f"\n📌 {rname}:\n"
            # Find subject name
            sid = m.get('subject_id')
            sname = next((s.get('subject_name') for s in subjects if s.get('id') == sid), f"Subject {sid}")
            mapping_info += f"  Step {m.get('step_order')}: {sname} - {m.get('note')}\n"
        
        return subject_info + roadmap_info + mapping_info
    
    @staticmethod
    def get_system_prompt():
        """Get system prompt with CSV context"""
        context = GroqService.build_context()
        
        return f"""Bạn là một AI tư vấn học tập thông minh cho sinh viên Việt Nam. 
Bạn có kiến thức về các môn học và lộ trình học tập trong hệ thống.

{context}

NHIỆM VỤ CỦA BẠN:
1. Phân tích thông tin sinh viên (năm học, GPA, số giờ học, mục tiêu nghề nghiệp, level)
2. Gợi ý lộ trình học tập phù hợp từ dữ liệu có sẵn
3. Đề xuất các môn học cụ thể với thứ tự hợp lý
4. Đưa ra lời khuyên cá nhân hóa

QUY TẮC TRẢ LỜI:
- Sử dụng emoji để làm nổi bật các phần
- Format đẹp với markdown
- Chia thành các section rõ ràng
- Luôn đề xuất ít nhất 1 lộ trình phù hợp
- Liệt kê các môn học theo thứ tự học
- Ước tính thời gian hoàn thành
- Đưa ra tips học tập thực tế
- Trả lời bằng tiếng Việt"""
    
    @staticmethod
    def recommend(user_data: dict, conversation_history: list = None):
        """
        Get AI recommendation based on user data
        
        Args:
            user_data: dict with year, gpa, study_time, goal, level, learning_mode
            conversation_history: list of previous messages for follow-up
        
        Returns:
            str: AI response
        """
        api_key = GroqService.get_api_key()
        if not api_key:
            return "❌ Lỗi: Chưa cấu hình GROQ_API_KEY trong file .env"
        
        messages = [
            {"role": "system", "content": GroqService.get_system_prompt()}
        ]
        
        # Add conversation history if exists
        if conversation_history:
            messages.extend(conversation_history)
        
        # Build user message
        if user_data:
            goal_mapping = {
                'it_software': 'Công nghệ thông tin / Phần mềm',
                'it_data': 'Dữ liệu / AI',
                'business': 'Kinh tế / Quản trị',
                'finance': 'Tài chính / Kế toán',
                'marketing': 'Marketing / Truyền thông',
                'engineering': 'Kỹ thuật / Công nghiệp',
                'education': 'Giáo dục / Sư phạm',
                'health': 'Y tế / Chăm sóc sức khỏe',
                'law': 'Luật',
                'social': 'Khoa học xã hội',
                'other': user_data.get('custom_goal', 'Khác')
            }
            
            level_mapping = {
                'beginner': 'Cơ bản',
                'intermediate': 'Trung cấp', 
                'advanced': 'Nâng cao'
            }
            
            goal_text = goal_mapping.get(user_data.get('goal'), user_data.get('goal'))
            level_text = level_mapping.get(user_data.get('level'), user_data.get('level'))
            
            user_message = f"""Hãy gợi ý lộ trình học tập cho sinh viên với thông tin:
            
📅 Năm học: {user_data.get('year')}
📊 GPA hiện tại: {user_data.get('gpa')}
⏰ Số giờ học/tuần: {user_data.get('study_time')} giờ
🎯 Mục tiêu nghề nghiệp: {goal_text}
📚 Trình độ hiện tại: {level_text}
💻 Hình thức học: {user_data.get('learning_mode', 'Chưa chọn')}
📖 Nguồn học: {user_data.get('resource', 'Chưa chọn')}

Hãy đề xuất lộ trình học tập chi tiết, phù hợp với điều kiện và mục tiêu của sinh viên này."""
            
            messages.append({"role": "user", "content": user_message})
        
        try:
            response = requests.post(
                GroqService.API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 4096
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"❌ Lỗi API: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "❌ Lỗi: Request timeout. Vui lòng thử lại."
        except Exception as e:
            return f"❌ Lỗi: {str(e)}"
    
    @staticmethod
    def chat(user_message: str, conversation_history: list):
        """
        Continue conversation with AI
        
        Args:
            user_message: User's follow-up question
            conversation_history: List of previous messages
            
        Returns:
            str: AI response
        """
        api_key = GroqService.get_api_key()
        if not api_key:
            return "❌ Lỗi: Chưa cấu hình GROQ_API_KEY trong file .env"
        
        messages = [
            {"role": "system", "content": GroqService.get_system_prompt()}
        ]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add new user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = requests.post(
                GroqService.API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 4096
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"❌ Lỗi API: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "❌ Lỗi: Request timeout. Vui lòng thử lại."
        except Exception as e:
            return f"❌ Lỗi: {str(e)}"
