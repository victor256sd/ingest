import streamlit as st
import streamlit_authenticator as stauth
import openai
from openai import OpenAI
import os
import time
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
from cryptography.fernet import Fernet
import re

# Disable the button called via on_click attribute.
def disable_button():
    st.session_state.disabled = True        

# Load config file with user credentials.
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# Definitive CSS selectors for Streamlit 1.45.1+
st.markdown("""
<style>
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    div[data-testid="stStatusWidget"] {
        visibility: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# Initiate authentication.
authenticator = stauth.Authenticate(
    config['credentials'],
)

# Call user login form.
result_auth = authenticator.login("main")
    
# If login successful, continue to aitam page.
if st.session_state.get('authentication_status'):
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{st.session_state.get('name')}* !')

    # Model list, Vector store ID, assistant IDs (one for initial upload eval, 
    # the second for follow-up user questions).
    # Removed: "gpt-4.1"
    MODEL_LIST = ["gpt-5-nano"] #"gpt-4.1-mini", "o4-mini", "gpt-4.1-nano", "gpt-4o-mini"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    VECTOR_STORE_ID = st.secrets["VECTOR_STORE_ID"]
    # INSTRUCTION_ENCRYPTED = b'gAAAAABof6jC28FjozJLLNjUdgMS5loA3arE9kWxx6wOYzudCPJC7kkMom8zayYcWZE7GvdfF3rLpm6oSBloBY0Udd-MdSekFwDkjoEfamzIzpHlB7OeCWR6xPTfXZsFdzsZpaEjItc0D2AUI_sXFtwSY8FJJXtOCEDul1wqP7n-x8CjDyrudtOGTUdsk0zreVdnjFRayc7e1stbUyLrOwGWxbXu7guUnBz9QMg4z860bjTnbmPim38yDyD3sCabHKoV6i1XpirRd_bnwobPHs1Fz5ZP7u4MxrJ26JmRARBhY2plN-swuabi7eg-hlHKVV8accXgBD0cAYlJ4POVBcDtL6Gx3hA1i-Hv6cI_jjn6ini-cBCQEXImm1Cl1BQx34nAAhgRmEvoae9SDKU5SE2hbkG_iP0Ju9igjogJ3zX97OGKvKdM3v-f-6BiFBQnkd_O0MrESYp8w1UO7T6Qyc8HOwCL6DmSv7vyf9xMCcyE6iuc6hqs3RpqsVvVrxCuGHhs-z-uc9MWZZ4iq23haO-uoA6-HuuzUy10G9mp2G_qkZl9fM6LnYlZ87gDulnLCOJX3hlPR3f4KYyCFYK_r8e8IwS_6m-S2tn0bgcYJhfC9uyqW6Ee6OsBZSryB0UtmMYlnxYxGPFZNRC_yI_hAkPESViBsR5hmrSZM3Rt0sif-u8kK_0RfdZkvsBIQDGh-oo6WOnYhHYvmGCtKWcTDVq3sYPsT6GtsnUR9EmCypHjGKV1FlZqgfqv75S9Fi20-WyQCc8TrvPrAmO0rIUs7C1xH8ZvNxQ-x6Jen7-0AXjTpQP_PoBCiGNWxa5mTVdDD6UYWetVw_XlMkdd6d1jIWrAolcS2ThhoiaTR-KS9XPEErw-Uvq4iOknFJRhTHmhpKAuxKsZ8CtqCTxfig3GsgriZJ59qkdxOJsLTCFWxTSTSGFahd1ZmNH2xY1KhjyYmMutL35ZKZxUTz5x9PNnpalC9h00u1rxRXsd7UE-GwGwzqgFPPzMhfg7oxq9K4M-bqWS9jK9tGCchQjAIu9wqYm2_1mmglDCkrzhqgDXz_0JwmuYyvjILnOxF_r_QY3NBNfivvexRsBHB5d4_yOGGRZ6wPx-y_huNCUlQgfP5NfzM4T4t5j5J81LpTfnytxGSc58g1Yup2foQRWEkF-IJL3oDf3MwTCSlvEwagpuF-ZnIW6ZbOzOcI5urrwWZ3vIupzfstqyO2qUxB4m-J3Iwkx_2X0vuZbbcK7W5Uwxh7uIWfQDTpIqBrJ27WtYWUxcunOocoq7FFUyG2euAcjlI0_m38kjQ-jU2YwP4h41sNEwjfZ7g0Hhm4k9UpzUtLLlP9aQ9lH_AmbeXCselnok8lQkMyXfXt5_3XbT5FH5VVn8TYjZcBGGPF2GQ0fxo0YaRhNMMYPjiI3j-BmI7ihhfgH-Vh7sSSy-wgd0dOZug7RRhOOz24e2KeHeDXAcLC1fO6dHkaAQ5CX3SNhjFoSilBeWHSFJDpQXl8JY5y4i1WgerbjQL2AivFR0pd2sigGUirUEjmvknQXtNnLXU2KyjnQbfAoNViizsRxM-hvrkoKXx0IX8psk1Hxp1cUm24cz7OJQrhmcVwCWcmVA4KR9mvp6zqg02oeNpXwzLleGfqUxyKjKjTZ0_O3SK8B91QwoRRxk0zktdMn-nlTHGVpvhuvEFodursp_h_c9OUNMFsOW41zyrDOM9IzG4maJMmnRcaXgBLzhOMpBGYBRwsUEG4spLcn1zR9sDcLariJex65JQ6kT8xJvuuGsHQhcWq9THNzePiAI-Rrgwb5UiIb-wGVnLIDfZqcQbBU3b_L1raGEfkXJ2iPYyee5VpPci259MVFrb4zG3r4utZltnMcItzjXxV1ZmPYT9he9Izqdc5D65FREdQOICKn4qOKOuayhvDgivswt9Pmpcu6_yOl_OM1d4tIkTuOwuL8xTrv8HgsV5vlFMf67H0Y67PRTt5ejkbD_iUKfOmrdLQUeCOI7i7tEbTMPf8GSeApbloQruerLruIowWfxAd8ugCcYLH51FhCX-7NUSAxREiElToBFdSdLORirXPScP4RB8itUSQ1-XQGYD9eT7pGmnB9dtKhPP6rKMmNIq_HHqGIknHGvPhyKG6nrwAscrzXST-xgO9db6hjzA759nHaNZPJn8BRNa8Lz9dWlPwVbqMHFihQyWFujZUnfM8CwYWmWQTqsVYp-MZMwAzn9Ku_Bs6Kh31xZtWT8yXtgtVNqGLP6nQsUmRA-TBtVtdscZucv9UKjOJM0LnuBfGHWXnL_iMgHbrFJEMSkJGoRRNvqstOkKoCvjn7FF8DFBS73WiwTkewSRTfKNZlnDZfUhQPJg13lzG1i6kNwc4iVfQJ5FjTrhg8ydmhRkta10xOOTqNOFi3QOzHwblkMMbUhu-7QlncjaWPIaxrfJwMKO9krj4_oKkvHaPWjXXG9aY3bF3kJtfZ5FCqm2RF5J6tgOgyB-TpE797n6Py4ghlhvFmqzEgU0xHgx0iEUVTj_82SfCXOVPhVZVEtvKIoof6-zml4bTWwVDGR2n6F65DjxGLy8v_-d00irzsKbf8ARlMeNo4AhVtcHyY4cMQNMihZEHOCSVuiv6PFl62FLrTrcTMyg1T8rFnjNU8hA3eD_Mgm-bVbITf8uA9tXYVTFPMtJC_mCIXnq4FkSr9wLwli7G-goscRc9GvZxG29NVeifQxHIo7DnKB-gVtMTaX_wR2FimtUUJokg3doGWmt-o_ffFyFP4faIrjQWZoZ2ja7067XZFnOqCmfi9qHVLwSo54VCigPia3_T_ojCY43wOIpUdMoxDcZ6wrXSbX9iWZt40zYCUWQrQlH9spMdRoCmkpP4deTEXN7QOmMcjWtZKGU_vN'    

    # key = st.secrets['INSTRUCTION_KEY'].encode()
    # f = Fernet(key)
    # INSTRUCTION = f.decrypt(INSTRUCTION_ENCRYPTED).decode()
    INSTRUCTION_ENCRYPTED = b'gAAAAABohnj6PA6fxhEekj1BIEcsfhLKo8twLZ-PVsRlhX8Ti_IzzoLA6MG4WPs0Ft3C4J0w3qLPkYm4dsudW6VObUNwYhZkWj3fF-wve7MiaV84LcCxFz-24yExEHvjEX5mvCVZLBONPimIJAdo4LBSi-VDYKXIqcrKDsppHd5xw6NOwx3GA47eCUeVVSfsFIHCz-cVaKFcB4EOXY4UBW1WIMSdmfF13N9l5xbgqM3pvrn-eokzJMB7GGtztcLPHnrKe1ZeZKEtcVlhUhWK3XyHxRvEYewXM5aCgKvqIi5W-lhASYcnKRTwOcR8-j8m-OdZwl58tzYjw5OvyWpqMB0-097YEdhwZirDvgkfJyiLC5k-b5xvO16liuUdSzNOYatxWKg3L87RIhIhPzP94hYep9Lnr8bw0A36mZssSkzbZd9Zntadx8XAA3VeQaOHkShoFKaJTXpBujkCgYcdtZF_wqPWpRzaTMF5t5FDSm1dvGOLiv5dgUVGBzf9ON56d_dwk6lg4mfJUo72QQlwWEHrhjKcHQMkgaaa5HFZQCCNiEAm-K3IzZGs96eSD5v0sRjBkbTb5c6-1DVNhOHd4e3SulENf97EeqF92FwBV-Q6iXgbA8aOQfUOvNy8uJXKIcjQygx2atUPxZ35JXxkG54TFFOi9AjqBHVHCEk03AekZpAjX996Tne86fTBgEWx-qToXfcihEu6uojpv-qoqT9OILPDU9b4JaUmLo6p-gHyRo_RTt2tOZoA4hTDblB5UyoDKIMq5CdyT9Jl2H5xmdcui924b5g3oJt-HNzpxlGxb2Ia5LlP-X-9xCTE0hGbiyrFSO0k-i5cVJx8u01g8OISc1dTbESfQuQ-w6I_Lcatp2o7K6Pb1JNDcBmMy-_Hb122tbTt0QIKW8PUzdk_17bG9Md1Hf-NBPfZYBusUeNWnFbMptpkWIJgenYU0k3uB-MNcUXasbliulyX-fmQ37CzD0EX8BXOmcgF1e5RpovhCklqgqRYU-okjxfulZ09VeIiQHCdxhJA5n3yNQKaxtNNA7nNEKs1Dh6ZnMjPAnQNvGTeNDuAvis0clgpX003Zm2pVhP9nnDu-MikcSXTiE-c11TihohzUiLArCpZGOBU_VGwRWz0-G1Js-B_V4hxDTWnn0T2LeMBcB0f_hMtkP7M25BxcPzXPX6v7qF5FZG-QzRkF6HlW966UTplopys32SzrzkBGZ0YmGv6_M6_9Bn8W8B6WQ6-lojk1IprWth8QQ8I7HUPQ_o7V1A5VmL0rcb8hRxNBc0mlulNb_vUeU_NNLQBVBtH2o250dLxbKY_ZlTtzxGv-cU0oJcDC16NVPEEdM_yPLX9hmBrQ7rSqH0j6Jsg5NXcubKygI_aYehOsuk0S_6WSRSvLywT04ni7paHIm085sBkaX7etjiVSFAf_s8xx3f-PtvLswCoLIY9Yr07bfDyhxrHU26BHPHs1WebJQOv9nKGNkaD3LD9EtvsQQ-6dmt0ZKF5p3ZVDUGW59fC405lLIdPgir1wlSl8sNeFgceGMheeAl5Tk9QzCIZTi1bUR8f6BgDssEZDn_WJOSEAxx-50clrPXOwOdFayct_GarHznbVHlR2_Gz1VZgQpiyVp92B0ymlfIaJ5eCTCcAj4msQdZKammTTsdBxD65Rayfhe4F_zWw36hT2j5G-7Qo09LOsNEBhH7AuXN25g0MeldoiyhF7Zy33AGIJioh_EkjzP3R7eMBiHMfj9-6aDsMkuEL2VCbUtApdL6HLSFN-vorVioGTD6w9CDoyW_KjwqMh32rDcT9HyXrqXzJSmbvl4U3yP17Z6jfnt5hZKKN33vpbcKZsajW7XuB6Xnq3PF3E6595GzKB8jZ7rojavfPuAfH_iPOhagBnS1EYUp9UWMkNVc8Ojtljpo5acybu_P-ilU05gpoaILuhM5cqNtm3_XFVA4S6T8o6iczhhN89pltqwibbeSRsn2OgcnRtvFXEKRxMlrPFGx-t6U7BB4VN0TFlAracA34tWyYwJCjudt2gnLn2BOKjCNjHgHjh5FsdFZFqZO5JGcoIty4u0TX6m7fuGGIOPJiqZYcOkB6BqdqkudsP1YQ9sxJxZQ1eD9ueb-HMVf9cw-8wSAyiNhFn1VsEfb-fYyu4VqqCacMe2881MLJZn7SUwBx-96EzbaS-ivJqD-YrFUmmLALrsRjfNOO633aol4qQyGDUqe-wRtmRqtuOLQ_s24zr8DGcIUiSlb33gbDq_h7bNtcnYaQUkYukA=='

    key = st.secrets['INSTRUCTION_KEY'].encode()
    f = Fernet(key)
    INSTRUCTION = f.decrypt(INSTRUCTION_ENCRYPTED).decode()

    
    # Set page layout and title.
    st.set_page_config(page_title="Ingest AI", page_icon=":space_invader:", layout="wide")
    st.header(":space_invader: Ingest AI")
    
    # Field for OpenAI API key.
    openai_api_key = os.environ.get("OPENAI_API_KEY", None)

    # Retrieve user-selected openai model.
    model: str = st.selectbox("Model", options=MODEL_LIST)
        
    # If there's no openai api key, stop.
    if not openai_api_key:
        st.error("Please enter your OpenAI API key!")
        st.stop()
    
    # Create new form to search aitam library vector store.    
    with st.form(key="qa_form", clear_on_submit=False):
        query = st.text_area("**Ask for ingest assistance:**")
        submit = st.form_submit_button("Send")
    # If submit button is clicked, query the aitam library.            
    if submit:
        # If form is submitted without a query, stop.
        if not query:
            st.error("No question submitted!")
            st.stop()            
        # Setup output columns to display results.
        # answer_col, sources_col = st.columns(2)
        # Create new client for this submission.
        client2 = OpenAI(api_key=openai_api_key)
        # Query the aitam library vector store and include internet
        # serach results.
        try:
            with st.spinner('Searching...'):
                response2 = client2.responses.create(
                    input = f"{INSTRUCTION}\n\n{query}",
                    model = model,
                    tools = [{
                                "type": "file_search",
                                "vector_store_ids": [VECTOR_STORE_ID],
                    }],
                    text={
                        "verbosity": "low"
                    },
                    reasoning={
                        "effort": "minimal"
                    },
                    include=["output[*].file_search_call.search_results"]
                )
        except:
            with st.spinner('Searching...'):
                response2 = client2.responses.create(
                    instructions = INSTRUCTION,
                    input = query,
                    model = model,
                    temperature = 0.6,
                    tools = [{
                                "type": "file_search",
                                "vector_store_ids": [VECTOR_STORE_ID],
                    }],
                    include=["output[*].file_search_call.search_results"]
                )
        # Write response to the answer column.    
        # with answer_col:
        if model == "gpt-5-nano":
              cleaned_response = re.sub(r'.*?', '', response2.output_text)
        else:
            # For o4-mini try, otherwise except.
            try:
                cleaned_response = re.sub(r'【.*?†.*?】', '', response2.output_text.strip())
            except:
                cleaned_response = re.sub(r'【.*?†.*?】', '', response2.output[1].content[0].text)
        st.markdown("#### Response")
        st.markdown(cleaned_response)
        # # Write files used to generate the answer.
        # with sources_col:
        #     if model != "o4-mini":
        #         st.markdown("#### Sources")
        #         # Extract annotations from the response, and print source files.
        #         annotations = response2.output[1].content[0].annotations
        #         retrieved_files = set([response2.filename for response2 in annotations])
        #         file_list_str = ", ".join(retrieved_files)
        #         st.markdown(f"**File(s):** {file_list_str}")

        #     if model == "o4-mini":
        #         input_tokens = 60000
        #         output_tokens = 5000
        #         total_tokens = 65000
        #         st.markdown("#### Approximate Token Usage")
        #     else:               
        #         input_tokens = response2.usage.input_tokens
        #         output_tokens = response2.usage.output_tokens
        #         total_tokens = input_tokens + output_tokens
        #         st.markdown("#### Token Usage")

        #     input_tokens_str = f"{input_tokens:,}"
        #     output_tokens_str = f"{output_tokens:,}"
        #     total_tokens_str = f"{total_tokens:,}"

        #     st.markdown(
        #         f"""
        #         <p style="margin-bottom:0;">Input Tokens: {input_tokens_str}</p>
        #         <p style="margin-bottom:0;">Output Tokens: {output_tokens_str}</p>
        #         """,
        #         unsafe_allow_html=True
        #     )
        #     st.markdown(f"Total Tokens: {total_tokens_str}")

        #     if model == "gpt-4.1-nano":
        #         input_token_cost = .1/1000000
        #         output_token_cost = .4/1000000
        #     elif model == "gpt-4o-mini":
        #         input_token_cost = .15/1000000
        #         output_token_cost = .6/1000000
        #     elif model == "gpt-4.1":
        #         input_token_cost = 2.00/1000000
        #         output_token_cost = 8.00/1000000
        #     elif model == "gpt-4.1-mini":
        #         input_token_cost = .4/1000000
        #         output_token_cost = 1.60/1000000
        #     elif model == "o4-mini":
        #         input_token_cost = 1.10/1000000
        #         output_token_cost = 4.40/1000000

        #     cost = input_tokens*input_token_cost + output_tokens*output_token_cost
        #     formatted_cost = "${:,.4f}".format(cost)
            
        #     st.markdown(f"**Total Cost:** {formatted_cost}")
            
elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')

elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')
