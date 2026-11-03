import { beforeEach, describe, expect, it, vi } from "vitest";

// api.js adresi yüklenirken okuduğu için import'tan önce ayarlanır
window.APP_CONFIG = { API_URL: "http://api.test" };
const { createTodo, deleteTodo, listTodos, updateTodo } = await import("./api.js");

const fetchMock = vi.fn();

function mockResponse(status, body) {
  fetchMock.mockResolvedValue({
    ok: status < 400,
    status,
    json: async () => body,
  });
}

describe("api", () => {
  beforeEach(() => {
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
  });

  it("listTodos adresi config.js'ten okur ve listeyi döner", async () => {
    mockResponse(200, [{ id: 1 }]);

    const todos = await listTodos();

    expect(fetchMock.mock.calls[0][0]).toBe("http://api.test/api/todos");
    expect(todos).toEqual([{ id: 1 }]);
  });

  it("createTodo başlığı POST ile gönderir", async () => {
    mockResponse(201, { id: 1, title: "süt al" });

    await createTodo("süt al");

    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toBe("http://api.test/api/todos");
    expect(options.method).toBe("POST");
    expect(JSON.parse(options.body)).toEqual({ title: "süt al" });
  });

  it("updateTodo değişiklikleri PATCH ile gönderir", async () => {
    mockResponse(200, { id: 5, completed: true });

    await updateTodo(5, { completed: true });

    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toBe("http://api.test/api/todos/5");
    expect(options.method).toBe("PATCH");
    expect(JSON.parse(options.body)).toEqual({ completed: true });
  });

  it("deleteTodo 204 yanıtında gövde okumadan null döner", async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      status: 204,
      json: async () => {
        throw new Error("204 yanıtında gövde yok");
      },
    });

    const result = await deleteTodo(5);

    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toBe("http://api.test/api/todos/5");
    expect(options.method).toBe("DELETE");
    expect(result).toBeNull();
  });

  it("başarısız yanıtta status koduyla hata fırlatır", async () => {
    mockResponse(500, {});

    await expect(listTodos()).rejects.toThrow("500");
  });
});
