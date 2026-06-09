import requests
import json
import os
import sys

def fetch_submissions(form_id, api_token):
    # 根据 Forminit 最新文档，Endpoint 应该是 /v1/forms 并通过 formId 过滤
    # 认证头使用 X-API-Key
    url = f"https://api.forminit.com/v1/forms?formId={form_id}"
    headers = {
        "X-API-Key": api_token,
        "Accept": "application/json"
    }
    
    print(f"Fetching submissions for form: {form_id}")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Forminit API 返回的数据结构通常在 'data' 字段中
        submissions = data.get('data', [])
        print(f"Successfully fetched {len(submissions)} submissions.")
        return submissions
    except Exception as e:
        print(f"Error fetching submissions: {e}")
        return []

def main():
    # 从环境变量获取敏感信息
    form_id = "sc1da0jaa4c"
    api_token = os.environ.get("FORMINIT_API_TOKEN")
    
    if not api_token:
        print("Error: FORMINIT_API_TOKEN environment variable not set.")
        sys.exit(1)
        
    submissions = fetch_submissions(form_id, api_token)
    
    # 提取有用的字段并保存
    comments = []
    for sub in submissions:
        # 获取表单字段内容
        answers = sub.get('answers', {})
        comment = {
            "name": answers.get('fi-sender-fullName', '匿名游客'),
            "email": answers.get('fi-sender-email', ''),
            "message": answers.get('fi-text-message', ''),
            "date": sub.get('created_at', ''),
            "attachment": answers.get('fi-file-attachment', '')
        }
        # 只保存有内容的留言
        if comment["message"]:
            comments.append(comment)
    
    # 确保目录存在
    os.makedirs("docs", exist_ok=True)
    
    # 保存为 JSON 文件，供前端调用
    output_path = "docs/comments.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
    
    print(f"Comments saved to {output_path}")

if __name__ == "__main__":
    main()
