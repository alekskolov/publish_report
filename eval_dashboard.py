import pprint
import re
import streamlit as st
import pandas as pd
import json
from streamlit.components.v1 import html

with open("report.jsonl", "r", encoding="utf-8") as f:
    lines = f.readlines()
    data = [json.loads(line) for line in lines]

final_data = {"Название промпта": [], "Оценка": [], "Промпт": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],
              "Диалог с ботом": [], "Оценка LLM": []}
samples_ids = []
tokens = []
ONE_TOKEN = 0.00002

for e in data:
    if 'data' in e:
        if e['type'] == 'metrics':
            final_data['Оценка'].append(e['data']['choice'])
            samples_ids.append(e['sample_id'])

for sample_id in samples_ids:
    for e in data:
        if 'data' in e:
            if e['type'] == 'sampling' and e['sample_id'] == sample_id and e['data']['prompt'][0]['role'] == "system":
                final_data['Промпт'].append(e['data']['prompt'][0]['content'])
                final_data['Диалог с ботом'].append(e['data']['sampled'][0])
                tokens.append(e['data']['usage']['total_tokens'])
            if e['type'] == 'sampling' and e['sample_id'] == sample_id and e['data']['prompt'][0]['role'] == "user":
                answer: str = e['data']['prompt'][0]['content']
                pattern = re.compile('Название промпта : (.+)')
                prompt_name = re.findall(pattern, answer)
                final_data["Название промпта"].append(prompt_name[0])
                final_data["Оценка LLM"].append(e['data']['sampled'][0])
                tokens.append(e['data']['usage']['total_tokens'])

# with open("C://Users//Al//PycharmProjects//evals//evals//registry//data//1test_dialog_bot//dialog.jsonl", "r",
#           encoding="utf-8") as f:
#     for line in f:
#         sample = json.loads(line)
#         final_data["Диалог с ботом"].append(sample['input'])

test_data_dict={}
with open("test_data.jsonl", "r",
          encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        name = item.get('name')
        input_text = item.get('input')
        if name and input_text:
            test_data_dict[name] = input_text
    for name in final_data["Название промпта"]:
        final_data['Диалог с ботом'].append(test_data_dict[name])


pprint.pprint(final_data)
df = pd.DataFrame(final_data)

if "selected_index" not in st.session_state:
    st.session_state.selected_index = None

if st.session_state.selected_index is not None:
    idx = st.session_state.selected_index
    st.markdown("### 🧾 Детали по промпту")
    st.write(f"**Название промпта:** {df['Название промпта'][idx]}")
    st.write(f"**Оценка:** {df['Оценка'][idx]}")
    with st.expander("Промпт"):
        st.markdown(df['Промпт'][idx])
    with st.expander("Диалог с ботом"):

        st.markdown("""
          <style>
          .chat-scroll {
              max-height: 400px;
              overflow-y: auto;
              padding: 10px;
              border: 1px solid #ccc;
              border-radius: 10px;
              background-color: #f9f9f9;
          }
          .chat-bubble {
              max-width: 80%;
              padding: 10px 15px;
              border-radius: 15px;
              margin: 5px;
              display: inline-block;
              font-size: 16px;
              line-height: 1.4;
          }
          .user {
              background-color: #DCF8C6;
              align-self: flex-end;
              margin-left: auto;
          }
          .bot {
              background-color: #E5E5EA;
              align-self: flex-start;
              margin-right: auto;
          }
          .chat-container {
              display: flex;
              flex-direction: column;
          }
          </style>
          """, unsafe_allow_html=True)


        def parse_dialog(raw_text):
            parts = []
            for line in raw_text.split(";"):
                line = line.strip()
                if not line:
                    continue
                if line.lower().startswith("бот :"):
                    speaker = "bot"
                    text = line.split(":", 1)[1].strip()
                elif line.lower().startswith("клиент :") or line.lower().startswith("user :"):
                    speaker = "user"
                    text = line.split(":", 1)[1].strip()
                else:
                    speaker = "user"
                    text = line.strip()
                parts.append((speaker, text))
            return parts


        parsed = parse_dialog(df['Диалог с ботом'][idx])

        # st.markdown('<div class="chat-scroll"><div class="chat-container">', unsafe_allow_html=True)
        # for role, msg in parsed:
        #     label = "👤 Клиент" if role == "user" else "🤖 Бот"
        #     bubble_class = "user" if role == "user" else "bot"
        #     st.markdown(
        #         f'<div class="chat-bubble {bubble_class}"><b>{label}:</b> {msg}</div>',
        #         unsafe_allow_html=True
        #     )
        # st.markdown('</div></div>', unsafe_allow_html=True)

        html_parts = """
                <style>
                .chat-scroll {
                    max-height: 400px;
                    overflow-y: auto;
                    padding: 10px;
                    border: 1px solid #ccc;
                    border-radius: 10px;
                    background-color: #f9f9f9;
                }
                .chat-bubble {
                    max-width: 80%;
                    padding: 10px 15px;
                    border-radius: 15px;
                    margin: 5px;
                    font-size: 16px;
                    line-height: 1.4;
                }
                .user {
                    background-color: #DCF8C6;
                    text-align: right;
                }
                .bot {
                    background-color: #E5E5EA;
                    text-align: left;
                }
                </style>
                <div class="chat-scroll">
                """

        for role, msg in parsed:
            label = "👤 Клиент" if role == "user" else "🤖 Бот"
            bubble_class = "user" if role == "user" else "bot"
            html_parts += f'<div class="chat-bubble {bubble_class}"><b>{label}:</b> {msg}</div>'

        html_parts += "</div>"

        html(html_parts, height=450)

    with st.expander("Оценка LLM"):
        st.markdown(df['Оценка LLM'][idx])

    if st.button("⬅️ Назад к таблице"):
        st.session_state.selected_index = None

else:
    st.markdown("### 📊 Табличный вид")

    header1, header2 = st.columns([4, 1])
    with header1:
        st.markdown("**Название промпта**")
    with header2:
        st.markdown("**Оценка**")

    for i, row in df.iterrows():
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(row["Название промпта"], key=f"prompt_{i}"):
                st.session_state.selected_index = i
        with col2:
            st.markdown(f"{row['Оценка']}")

    st.write(f"**Всего потрачено токенов :** {sum(tokens)} ≈ {sum(tokens) * ONE_TOKEN}$ ")
# st.dataframe(df)
#

# with open("eval_logA.jsonl", "r", encoding="utf-8") as f:
#     entries = [json.loads(line) for line in f]
#
# pprint.pprint(entries)
#
#
#
#
# rows = []
# pprint.pprint(entries)
#
# df = pd.DataFrame(rows)
# st.dataframe(df, use_container_width=True)

# for e in entries:
#     pprint.pprint(e)
# rows = []
# for e in entries:
#     if '"type": "sampling"' in e:
#         data = e['data']
#         rows.append({
#             "Prompt": data['prompt'][0]['content'],
#             "Response": data['sampled'][0],
#             "Model": e['data'].get('model', 'unknown'),
#             "Total Tokens": data['usage']['total_tokens'],
#         })
#
# df = pd.DataFrame(rows)
#
# # UI
# st.title("📊 OpenAI Evals Report")
# st.dataframe(df, use_container_width=True)
#
# with st.expander("📈 Summary"):
#     st.write(df.describe())
