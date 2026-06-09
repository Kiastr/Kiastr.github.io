import requests
import json
import os
import sys

def fetch_submissions(form_id, api_token):
    # Forminit REST API 在免费计划下可能受限 (403 Forbidden)
    url = f"https://api.forminit.com/v1/forms/{form_id}"
    headers = {
        "X-API-Key": api_token,
        "Accept": "application/json"
    }
    
    print(f"Fetching submissions for form: {form_id}")
    try:
        response = requests.get(url, headers=headers)
        
        # 优雅处理 403/401 错误，不中断构建流程
        if response.status_code in [401, 403]:
            print(f"Warning: API returned {response.status_code}. This is likely due to Free Plan limitations on REST API access.")
            print("Action: Keeping existing comments.json. You can manually update it if needed.")
            return None
            
        response.raise_for_status()
        result = response.json()
        
        # 解析响应数据
        data_obj = result.get('data', {})
        submissions = data_obj.get('submissions', [])
        
        print(f"Successfully fetched {len(submissions)} submissions.")
        return submissions
    except Exception as e:
        print(f"Error fetching submissions: {e}")
        return None

def main():
    form_id = "injiglxlx41"
    api_token = os.environ.get("FORMINIT_API_TOKEN")
    
    # 如果没有设置 Token，也视为同步失败但正常退出
    if not api_token:
        print("Warning: FORMINIT_API_TOKEN environment variable not set. Skipping sync.")
        return
        
    submissions = fetch_submissions(form_id, api_token)
    
    output_path = "docs/comments.json"
    os.makedirs("docs", exist_ok=True)
    
    # 如果 API 调用失败，保持现有文件
    if submissions is None:
        if not os.path.exists(output_path):
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump([], f)
        return

    comments = []
    for sub in submissions:
        blocks = sub.get('blocks', {})
        sender = blocks.get('sender', {})
        
        # 兼容多种可能的字段名映射
        comment = {
            "name": sender.get('fullName') or blocks.get('fi-sender-fullName') or '匿名游客',
            "email": sender.get('email') or blocks.get('fi-sender-email') or '',
            "message": blocks.get('message') or blocks.get('fi-text-message') or blocks.get('comments') or '',
            "date": sub.get('submissionDate', '') or sub.get('created_at', '')
        }
        
        if comment["message"]:
            comments.append(comment)
    
    # 按时间倒序排列
    try:
        comments.sort(key=lambda x: x['date'], reverse=True)
    except:
        pass

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
    
    print(f"Comments saved to {output_path} (Total: {len(comments)})")

if __name__ == "__main__":
    main()
