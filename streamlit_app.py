import os
import json
from typing import Any, Dict, Optional

import requests
import streamlit as st


def get_base_url() -> str:
	default_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
	return st.sidebar.text_input("API Base URL", value=default_url, help="Base URL of the FastAPI server")


def get_health(base_url: str) -> Optional[Dict[str, Any]]:
	try:
		resp = requests.get(f"{base_url}/health", timeout=10)
		resp.raise_for_status()
		return resp.json()
	except requests.RequestException as exc:
		st.error(f"Health check failed: {exc}")
		return None


def post_json(base_url: str, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
	try:
		resp = requests.post(f"{base_url}{endpoint}", json=payload, timeout=60)
		resp.raise_for_status()
		return resp.json()
	except requests.HTTPError as exc:
		# Try to show server-provided error details
		try:
			data = resp.json()
			st.error(f"Request failed: {resp.status_code} - {json.dumps(data, indent=2)}")
		except Exception:
			st.error(f"Request failed: {exc}")
		return None
	except requests.RequestException as exc:
		st.error(f"Request error: {exc}")
		return None


def render_health_section(base_url: str) -> None:
	st.subheader("API Health")
	col1, col2 = st.columns([1, 3])
	with col1:
		if st.button("Check Health"):
			result = get_health(base_url)
			with col2:
				if result is not None:
					st.success("API is reachable")
					st.json(result)


def render_ingest_tab(base_url: str) -> None:
	st.header("Ingest PDF")
	st.caption("The API currently expects a server-accessible file path.")

	namespace = st.text_input("Namespace (optional)")
	pdf_path = st.text_input(
		"PDF path on server",
		help="Absolute or relative path on the API server host",
	)
	col_a, col_b = st.columns(2)
	with col_a:
		chunk_size = st.number_input("Chunk size", min_value=100, max_value=8000, value=1000, step=50)
	with col_b:
		chunk_overlap = st.number_input("Chunk overlap", min_value=0, max_value=1000, value=150, step=10)

	if st.button("Run Ingest", type="primary"):
		if not pdf_path:
			st.warning("Please provide a PDF path.")
			return
		payload = {
			"pdf_path": pdf_path,
			"namespace": namespace or None,
			"chunk_size": int(chunk_size),
			"chunk_overlap": int(chunk_overlap),
		}
		with st.spinner("Ingesting... this may take a moment"):
			data = post_json(base_url, "/ingest", payload)
			if data is not None:
				st.success("Ingest completed")
				st.json(data)


def render_chat_tab(base_url: str) -> None:
	st.header("Chat")
	if "chat_history" not in st.session_state:
		st.session_state.chat_history = []

	namespace = st.text_input("Namespace (optional)", key="chat_namespace")
	k = st.number_input("Top K context chunks", min_value=1, max_value=20, value=5, step=1)
	question = st.text_area("Your question", placeholder="Ask about your documents or products...")

	if st.button("Ask", type="primary"):
		if not question.strip():
			st.warning("Please enter a question.")
			return
		payload = {"question": question.strip(), "namespace": namespace or None, "k": int(k)}
		with st.spinner("Thinking..."):
			data = post_json(base_url, "/chat", payload)
			if data is not None:
				st.session_state.chat_history.append({"role": "user", "content": question})
				st.session_state.chat_history.append({"role": "assistant", "content": data.get("answer", "")})
				st.success("Answer received")
				st.subheader("Answer")
				st.write(data.get("answer", ""))
				if data.get("products"):
					st.subheader("Products")
					st.json(data["products"])
				if data.get("sources"):
					st.subheader("Sources")
					st.json(data["sources"])

	if st.session_state.chat_history:
		with st.expander("Conversation history"):
			for turn in st.session_state.chat_history:
				role = turn.get("role", "")
				content = turn.get("content", "")
				st.markdown(f"**{role.capitalize()}:** {content}")


def main() -> None:
	st.set_page_config(page_title="RAG API Tester", page_icon="💬", layout="wide")
	st.title("RAG API Tester")

	base_url = get_base_url()
	render_health_section(base_url)

	tab_chat, tab_ingest = st.tabs(["Chat", "Ingest"])
	with tab_chat:
		render_chat_tab(base_url)
	with tab_ingest:
		render_ingest_tab(base_url)


if __name__ == "__main__":
	main()


