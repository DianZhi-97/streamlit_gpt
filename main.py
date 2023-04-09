import streamlit as st
import json
import streamlit_authenticator as stauth
import openai
from streamlit_chat import message

# config the page title and icon
st.set_page_config(page_title='GPT', page_icon='🤖', layout='wide')

# format page styles
style = '''
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
'''

st.markdown(style, unsafe_allow_html=True)

# load registered user info
credentials = json.loads(st.secrets['authetications']['credentials'])

# config the auhenticator
authenticator = stauth.Authenticate(
    credentials,
    st.secrets['cookie']['name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days']
)

# start the authenticator
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
else:
    # get OpenAI API key
    openai.api_key = st.secrets['openai_apikey']

    # init session states
    if 'generated_response' not in st.session_state:
        st.session_state.generated_response = []
    if 'past_prompt' not in st.session_state:
        st.session_state.past_prompt = []
    if 'conversation' not in st.session_state:
        st.session_state.conversation = [{'role': 'system', 'content': 'You are GPT, a large language model trained by OpenAI. Answer as concisely as possible.'}]

    # reset the conversation history
    def reset_conversation():
        st.session_state.generated_response = []
        st.session_state.past_prompt = []
        st.session_state.conversation = [{'role': 'system', 'content': 'You are GPT, a large language model trained by OpenAI. Answer as concisely as possible.'}]

    # takes a list of conversation and temperature and get response text
    def query(conversation, temperature, model):
        response = openai.ChatCompletion.create(
            # model="gpt-4",
            model=model,
            messages=conversation,
            temperature=temperature)
        return response['choices'][0]['message']['content']

    # use form to gather user input
    def get_input():
        with st.form('get_text_input', clear_on_submit=True):
            user_input = st.text_area('输入对话内容:', '')
            submitted = st.form_submit_button('发送')
        if submitted:
            return user_input

    # sidebar
    with st.sidebar:
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader(name + ', Welcome:tada:')
        with col_right:
            authenticator.logout('退出登陆')
        st.selectbox('选择您想使用的模型', ('gpt-4', 'gpt-3.5-turbo'), key='model', on_change=reset_conversation)
        temperature = st.slider('Temperature', min_value=0.0, max_value=2.0, value=0.5, step=0.05)
        st.write('Tips: 更高的Temperature会使GPT的回答更加多样化')    

    st.title('OpenAI GPT')
    
    col_left, col_right = st.columns([8,1])
    with col_left:
        st.write('本App直接调用了OpenAI的GPT API [OpenAI GPT 入口](https://openai.com/product/gpt-4)')
    with col_right:
        st.button('清空对话', on_click=reset_conversation)
    
    # text input
    user_input = get_input()

    # format and send query to OpenAI API and get response
    if user_input:
        with st.spinner('生成中...'):
            st.session_state.conversation.append({'role': 'user', 'content': user_input})
            output = query(st.session_state.conversation, temperature, st.session_state.model)
            st.session_state.past_prompt.append(user_input)
            st.session_state.generated_response.append(output)
            st.session_state.conversation.append({'role': 'assistant', 'content': output})

    # display the chat history
    if st.session_state['generated_response']:
        for i in range(len(st.session_state['generated_response'])-1, -1, -1):
            message(st.session_state['generated_response'][i], key=str(i), 
            avatar_style='bottts', seed='ChatGPT')
            message(st.session_state['past_prompt'][i], is_user=True, key=str(i) + '_user', 
            avatar_style='initials', seed=name[0])