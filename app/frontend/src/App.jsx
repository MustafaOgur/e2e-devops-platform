import { useEffect, useState } from "react";

import { createTodo, deleteTodo, listTodos, updateTodo } from "./api.js";

export default function App() {
  const [todos, setTodos] = useState([]);
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    listTodos()
      .then(setTodos)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function run(action) {
    setError(null);
    try {
      await action();
    } catch (err) {
      setError(err.message);
    }
  }

  function handleAdd(event) {
    event.preventDefault();
    const trimmed = title.trim();
    if (!trimmed) return;
    void run(async () => {
      const todo = await createTodo(trimmed);
      setTodos((current) => [todo, ...current]);
      setTitle("");
    });
  }

  function handleToggle(todo) {
    void run(async () => {
      const updated = await updateTodo(todo.id, { completed: !todo.completed });
      setTodos((current) =>
        current.map((item) => (item.id === updated.id ? updated : item)),
      );
    });
  }

  function handleDelete(id) {
    void run(async () => {
      await deleteTodo(id);
      setTodos((current) => current.filter((item) => item.id !== id));
    });
  }

  return (
    <main className="container">
      <h1>Todo</h1>

      <form className="add-form" onSubmit={handleAdd}>
        <input
          aria-label="Yeni görev"
          placeholder="Yeni görev..."
          maxLength={200}
          value={title}
          onChange={(event) => setTitle(event.target.value)}
        />
        <button type="submit">Ekle</button>
      </form>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      {loading && <p className="muted">Yükleniyor...</p>}
      {!loading && !error && todos.length === 0 && (
        <p className="muted">Henüz görev yok.</p>
      )}

      <ul className="todo-list">
        {todos.map((todo) => (
          <li key={todo.id} className="todo-item">
            <label className={todo.completed ? "done" : undefined}>
              <input
                type="checkbox"
                checked={todo.completed}
                onChange={() => handleToggle(todo)}
              />
              <span>{todo.title}</span>
            </label>
            <button className="delete" onClick={() => handleDelete(todo.id)}>
              Sil
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}
