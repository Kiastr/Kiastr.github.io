import requests
import json
import os
import sys

def fetch_submissions(form_id, api_token):
    # 实测验证成功的 Endpoint：api.forminit.com/v1/forms/{formId}
    # 认证头使用 X-API-Key
    url = f"https://api.forminit.com/v1/forms/{form_id}"
    headers = {
        "X-API-Key": api_token,
        "Accept": "application/json"
    }
    
    print(f"Fetching submissions for form: {form_id}")
    try:
        response = requests.get(url, headers=headers)
        
        # 处理 403 错误（通常是因为表单中还有残留的文件上传字段导致免费计划报错）
        if response.status_code == 403:
            print("Error: 403 Forbidden. This is likely because file uploads are enabled on a Free Plan.")
            print("Please ensure you have removed the file upload block from your Forminit dashboard.")
            return []
            
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
    form_id = "injiglxlx41"
    api_token = os.environ.get("FORMINIT_API_TOKEN")
    
    if not api_token:
        print("Error: FORMINIT_API_TOKEN environment variable not set.")
        sys.exit(1)
        
    submissions = fetch_submissions(form_id, api_token)
    
    comments = []
    for sub in submissions:
        answers = sub.get('answers', {})
        comment = {
            "name": answers.get('fi-sender-fullName', '匿名游客'),
            "email": answers.get('fi-sender-email', ''),
            "message": answers.get('fi-text-message', ''),
            "date": sub.get('created_at', '')
        }
        if comment["message"]:
            comments.append(comment)
    
    os.makedirs("docs", exist_ok=True)
    output_path = "docs/comments.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
    
    print(f"Comments saved to {output_path}")

if __name__ == "__main__":
    main()
