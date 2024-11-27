from search import *
import streamlit as st
import time

@st.cache_resource
def load_data(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

class SearchEngine:
    def __init__(self,data1, data2) -> None:
        self.data1 = data1
        self.data2 = data2
        self.queries = None
        self.time = None

    def main(self):
        if 'result' not in st.session_state:
            st.session_state.result = None
        self.message_input()
        self.create_search_ui()

    def create_search_ui(self):
        if st.session_state.result is not None:
            if len(st.session_state.result) == 0:
                st.write('NO RELATED URL')
            if len(st.session_state.result)>15:
                st.write(f'This shows TOP 15 out of {len(st.session_state.result)} related URL')
                for i in range(15):
                    st.write(f"{i+1}: {st.session_state.result[i]}")
            else:
                for i in range(len(st.session_state.result)):
                    st.write(f"{i+1}: {st.session_state.result[i]}")

    def message_input(self):
        st.title('Search Engine')
        with st.container():
            def on_enter():
                self.queries = st.session_state["Keyword"]
                self.search_result()

            message_input = st.text_input("Type Search Keyword Here", key="Keyword", on_change=on_enter)
            self.queries = message_input
            if st.button("Enter", key="enter"):
                on_enter()
                st.rerun()

    def search_result(self):
        with open("./index.txt", 'r', encoding='utf-8') as file:
            a = time.time()
            st.session_state.result = search(self.queries,self.data1,self.data2, file)
            b = time.time()
            print(b-a)

if __name__ == "__main__":
    data1 = r'.\secondary_index.json' #local index.json
    data2 = r".\docid_map.json" #local docid.json
    data1 = load_data(data1)
    data2 = load_data(data2)
    engine = SearchEngine(data1, data2)
    engine.main()