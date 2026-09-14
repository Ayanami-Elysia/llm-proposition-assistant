"""
文心一言大模型工具类
用于智能命题、难度评估、知识点分析等功能
"""
import requests
import json
from config.config import WENXIN_BEARER_TOKEN, WENXIN_API_URL, WENXIN_MODEL


class WenxinAIService:
    """文心一言AI服务类"""
    
    @staticmethod
    def _call_wenxin_api(messages, temperature=0.7, max_tokens=2000):
        """
        调用文心一言API
        
        Args:
            messages: 消息列表，格式：[{"role": "user", "content": "..."}]
            temperature: 温度参数，控制随机性 (0-1)
            max_tokens: 最大生成token数（千帆v2使用max_completion_tokens，范围1-2048）
            
        Returns:
            str: AI返回的文本内容
        """
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {WENXIN_BEARER_TOKEN}'
            }
            
            # 确保max_tokens在有效范围内 [1, 2048]
            if max_tokens > 2048:
                max_tokens = 2048
            elif max_tokens < 1:
                max_tokens = 1000
            
            payload = {
                'model': WENXIN_MODEL,
                'messages': messages,
                'temperature': temperature,
                'max_completion_tokens': max_tokens  # 千帆v2使用max_completion_tokens
            }
            
            print(f"调用文心一言API: {WENXIN_API_URL}")
            print(f"请求参数: {json.dumps(payload, ensure_ascii=False)}")
            
            response = requests.post(
                WENXIN_API_URL,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                # 千帆v2格式
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0].get('message', {}).get('content', '')
                    return content
                # 兼容其他格式
                elif 'result' in result:
                    return result['result']
                else:
                    raise Exception(f"API返回格式异常: {result}")
            else:
                raise Exception(f"API调用失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"调用文心一言API失败: {str(e)}")
            raise e
    
    @staticmethod
    def generate_question(subject, grade, knowledge_points, question_type, count=1):
        """
        智能生成试题（AI自动评估难度）
        
        Args:
            subject: 学科（如：数学、语文、英语）
            grade: 年级（如：一年级、二年级）
            knowledge_points: 知识点范围（字符串，多个用逗号分隔）
            question_type: 题型（single_choice/multiple_choice/fill_blank/essay/judge）
            count: 生成题目数量
            
        Returns:
            list: 生成的题目列表，每个题目包含content、options、answer、analysis、difficulty等字段
        """
        question_type_map = {
            'single_choice': '单选题',
            'multiple_choice': '多选题',
            'fill_blank': '填空题',
            'essay': '解答题',
            'judge': '判断题'
        }
        
        question_type_name = question_type_map.get(question_type, question_type)
        
        # 构建提示词
        prompt = f"""你是一位资深的{subject}教师，请根据以下要求生成{count}道高质量的试题：

学科：{subject}
年级：{grade}
知识点范围：{knowledge_points}
题型：{question_type_name}

要求：
1. 题目内容要符合{grade}学生的认知水平
2. 题目要紧扣指定的知识点：{knowledge_points}
3. 题目难度要适中，并自动评估每道题的难度
4. 题目表述要清晰、准确、无歧义
5. 必须提供准确的答案和详细的解析
6. 必须分析题目涉及的知识点
7. 必须评估题目的难度等级和难度系数

请严格按照以下JSON格式返回（直接返回JSON，不要有其他文字）：
"""

        if question_type == 'single_choice':
            prompt += """
[
  {
    "content": "题目内容",
    "optionA": "选项A内容",
    "optionB": "选项B内容",
    "optionC": "选项C内容",
    "optionD": "选项D内容",
    "correctAnswer": "A",
    "analysis": "详细解析，说明解题思路和方法",
    "knowledgePoints": ["知识点1", "知识点2"],
    "difficultyLevel": "中等",
    "difficultyScore": "0.5",
    "difficultyAnalysis": "从知识点复杂度、思维能力、计算量等维度分析难度"
  }
]
"""
        elif question_type == 'multiple_choice':
            prompt += """
[
  {
    "content": "题目内容",
    "optionA": "选项A内容",
    "optionB": "选项B内容",
    "optionC": "选项C内容",
    "optionD": "选项D内容",
    "correctAnswer": "A,C",
    "analysis": "详细解析，说明为什么选择这些选项",
    "knowledgePoints": ["知识点1", "知识点2"],
    "difficultyLevel": "中等",
    "difficultyScore": "0.5",
    "difficultyAnalysis": "从知识点复杂度、思维能力、计算量等维度分析难度"
  }
]
"""
        elif question_type == 'judge':
            prompt += """
[
  {
    "content": "题目内容（判断对错）",
    "optionA": "正确",
    "optionB": "错误",
    "correctAnswer": "A",
    "analysis": "详细解析，说明判断依据",
    "knowledgePoints": ["知识点1", "知识点2"],
    "difficultyLevel": "简单",
    "difficultyScore": "0.3",
    "difficultyAnalysis": "从知识点复杂度、思维能力、计算量等维度分析难度"
  }
]
"""
        elif question_type == 'fill_blank':
            prompt += """
[
  {
    "content": "题目内容（用____表示填空位置）",
    "correctAnswer": "正确答案",
    "analysis": "详细解析，说明解题思路",
    "knowledgePoints": ["知识点1", "知识点2"],
    "difficultyLevel": "中等",
    "difficultyScore": "0.5",
    "difficultyAnalysis": "从知识点复杂度、思维能力、计算量等维度分析难度"
  }
]
"""
        elif question_type == 'essay':
            prompt += """
[
  {
    "content": "题目内容",
    "correctAnswer": "参考答案或解题步骤",
    "analysis": "详细解析，包括解题思路、关键步骤、注意事项等",
    "knowledgePoints": ["知识点1", "知识点2"],
    "difficultyLevel": "困难",
    "difficultyScore": "0.7",
    "difficultyAnalysis": "从知识点复杂度、思维能力、计算量等维度分析难度"
  }
]
"""
        
        prompt += """
注意：
- difficultyLevel: 难度等级，可选值：简单、中等、困难
- difficultyScore: 难度系数，范围0-1，0.3以下为简单，0.3-0.7为中等，0.7以上为困难
- knowledgePoints: 题目涉及的知识点列表
- difficultyAnalysis: 详细的难度分析说明
"""
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response_text = WenxinAIService._call_wenxin_api(messages, temperature=0.8, max_tokens=2000)
            
            # 尝试解析JSON
            # 清理可能的markdown代码块标记
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            questions = json.loads(response_text)
            
            # 确保返回的是列表
            if not isinstance(questions, list):
                questions = [questions]
            
            return questions
            
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {str(e)}, 原始响应: {response_text}")
            raise Exception(f"AI返回的内容格式不正确，无法解析为JSON")
        except Exception as e:
            print(f"生成题目失败: {str(e)}")
            raise e
    
    @staticmethod
    def evaluate_difficulty(content, question_type, subject, grade, options=None):
        """
        评估试题难度
        
        Args:
            content: 题目内容
            question_type: 题型
            subject: 学科
            grade: 年级
            options: 选项（字典，如 {"A": "...", "B": "..."}）
            
        Returns:
            dict: 包含difficulty（难度系数）、level（难度等级）、analysis（分析说明）
        """
        question_type_map = {
            'single_choice': '单选题',
            'multiple_choice': '多选题',
            'fill_blank': '填空题',
            'essay': '解答题',
            'judge': '判断题'
        }
        
        question_type_name = question_type_map.get(question_type, question_type)
        
        options_text = ""
        if options:
            for key, value in options.items():
                if value:
                    options_text += f"\n{key}. {value}"
        
        prompt = f"""你是一位资深的{subject}教育专家，请对以下试题进行难度评估：

学科：{subject}
年级：{grade}
题型：{question_type_name}

题目内容：
{content}
{options_text}

请从以下维度进行分析：
1. 知识点的复杂程度
2. 解题所需的思维能力（记忆、理解、应用、分析、综合、评价）
3. 计算量或推理步骤的多少
4. 对{grade}学生而言的认知难度

请严格按照以下JSON格式返回（直接返回JSON，不要有其他文字）：
{{
  "difficulty": 0.65,
  "level": "中等",
  "analysis": "详细的难度分析说明，包括各个维度的评估理由"
}}

说明：
- difficulty: 难度系数，范围0-1，0.3以下为简单，0.3-0.7为中等，0.7以上为困难
- level: 难度等级，可选值：简单、中等、困难
- analysis: 详细分析，说明为什么给出这个难度评估
"""
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response_text = WenxinAIService._call_wenxin_api(messages, temperature=0.5, max_tokens=1000)
            
            # 清理markdown标记
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            
            # 验证返回格式
            if 'difficulty' not in result or 'level' not in result or 'analysis' not in result:
                raise Exception("AI返回的难度评估格式不完整")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {str(e)}, 原始响应: {response_text}")
            raise Exception(f"AI返回的内容格式不正确，无法解析为JSON")
        except Exception as e:
            print(f"评估难度失败: {str(e)}")
            raise e
    
    @staticmethod
    def analyze_knowledge_points(content, question_type, subject, grade, options=None):
        """
        分析试题涉及的知识点
        
        Args:
            content: 题目内容
            question_type: 题型
            subject: 学科
            grade: 年级
            options: 选项
            
        Returns:
            dict: 包含knowledge_points（知识点列表）、analysis（分析说明）
        """
        question_type_map = {
            'single_choice': '单选题',
            'multiple_choice': '多选题',
            'fill_blank': '填空题',
            'essay': '解答题',
            'judge': '判断题'
        }
        
        question_type_name = question_type_map.get(question_type, question_type)
        
        options_text = ""
        if options:
            for key, value in options.items():
                if value:
                    options_text += f"\n{key}. {value}"
        
        prompt = f"""你是一位资深的{subject}教育专家，请分析以下试题涉及的知识点：

学科：{subject}
年级：{grade}
题型：{question_type_name}

题目内容：
{content}
{options_text}

请识别该题目涉及的所有知识点，并说明每个知识点在题目中的体现。

请严格按照以下JSON格式返回（直接返回JSON，不要有其他文字）：
{{
  "knowledge_points": ["知识点1", "知识点2", "知识点3"],
  "analysis": "详细分析说明，解释题目如何考查这些知识点，以及各知识点之间的关联"
}}
"""
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response_text = WenxinAIService._call_wenxin_api(messages, temperature=0.5, max_tokens=1000)
            
            # 清理markdown标记
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            
            # 验证返回格式
            if 'knowledge_points' not in result or 'analysis' not in result:
                raise Exception("AI返回的知识点分析格式不完整")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {str(e)}, 原始响应: {response_text}")
            raise Exception(f"AI返回的内容格式不正确，无法解析为JSON")
        except Exception as e:
            print(f"分析知识点失败: {str(e)}")
            raise e

