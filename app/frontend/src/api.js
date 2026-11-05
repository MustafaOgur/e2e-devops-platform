const BASE_URL = `${window.APP_CONFIG?.API_URL ?? ""}/api/todos`;

async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`İstek başarısız oldu (${response.status})`);
  }
  return response.status === 204 ? null : response.json();
}

export const listTodos = () => request("");

export const createTodo = (title) =>
  request("", { method: "POST", body: JSON.stringify({ title }) });

export const updateTodo = (id, changes) =>
  request(`/${encodeURIComponent(id)}`, { method: "PATCH", body: JSON.stringify(changes) });

export const deleteTodo = (id) => request(`/${encodeURIComponent(id)}`, { method: "DELETE" });
