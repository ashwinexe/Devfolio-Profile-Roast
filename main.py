from dotenv import load_dotenv
from flask import Flask, render_template, request
from jigsawstack import JigsawStack, JigsawStackError
import os
app = Flask(__name__)

API_KEY = os.environ.get('JIGSAWSTACK_API_KEY')

@app.route('/', methods=['GET', 'POST'])
def index():
    summary = ""
    if request.method == 'POST':
        input_url = request.form.get('input_url', '')
        jigsaw = JigsawStack(api_key=API_KEY)

        try:
            if input_url:
                result = jigsaw.web.ai_scrape({
                    "url": input_url,
                    "element_prompts": ["projectItem"],
                })
                text = ""
                for item in result.get('data',[]):
                    text += item['results'][0].get('text', '')
                if text:
                    summary_result = jigsaw.summary({"text": text})
                    summary = summary_result.get('summary', '')
                    
                    # Limit the summary to 300 characters due to JigsawStack API limitations
                    summary = summary[:250]
                    print('summary: ', summary)
                else:
                    summary = "Your Portfolio is empty! Start by participating in few Hackathosn at Devfolio."
        except JigsawStackError as e:
            text = e.message

        # Roast the summary
        params = {
            "prompt": "Do a profile roast about this developer:{about}. Avoid newline and special characters.",
            "inputs": [
                {
                    "key": "about",
                },
            ],
            "return_prompt": "Return the result in a plain text format",
           }
        prompt_id = jigsaw.prompt_engine.create(params)
        print(prompt_id)
        roast_id = prompt_id.get('prompt_engine_id')
        result = jigsaw.prompt_engine.run(
        {
            "id": roast_id,
            "input_values": {
                "about": summary,
            },
        }
    )
        print(type(result))
        summary = result.get('result', '')
    return render_template('index.html', summary=summary)

# def roast(summary, jigsaw):

#     params = {
#     "prompt": "Do a profile roast about this developer: {about}",
#     "inputs": [
#         {
#             "key": "about",
#         },
#     ],
#     "return_prompt": "Return the result in a markdown format",
#     "prompt_guard": ["sexual_content", "defamation"]
# }
#     prompt_id = jigsaw.prompt_engine.create(params)
#     print(prompt_id)
#     roast_id = prompt_id.get('prompt_engine_id')
#     result = jigsawstack.prompt_engine.run(
#     {
#         "id": {roast_id},
#         "input_values": {
#             about: summary,
#         },
#     }
# )
#     print(result)
#     return result

#local testing
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
