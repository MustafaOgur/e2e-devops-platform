import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App.jsx";
import { createTodo, deleteTodo, listTodos, updateTodo } from "./api.js";

vi.mock("./api.js");

const milk = { id: 1, title: "süt al", completed: false };
const bread = { id: 2, title: "ekmek al", completed: true };

describe("App", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    listTodos.mockResolvedValue([]);
  });

  it("görev yoksa boş durum mesajını gösterir", async () => {
    render(<App />);

    expect(await screen.findByText("Henüz görev yok.")).toBeInTheDocument();
    expect(screen.queryByText("Yükleniyor...")).not.toBeInTheDocument();
  });

  it("görevleri ve tamamlanma durumlarını listeler", async () => {
    listTodos.mockResolvedValue([bread, milk]);

    render(<App />);

    expect(await screen.findByRole("checkbox", { name: "ekmek al" })).toBeChecked();
    expect(screen.getByRole("checkbox", { name: "süt al" })).not.toBeChecked();
  });

  it("liste yüklenemezse hatayı gösterir", async () => {
    listTodos.mockRejectedValue(new Error("İstek başarısız oldu (500)"));

    render(<App />);

    expect(await screen.findByRole("alert")).toHaveTextContent("(500)");
    expect(screen.queryByText("Henüz görev yok.")).not.toBeInTheDocument();
  });

  it("yeni görevi kırpıp ekler, listenin başına koyar ve girişi temizler", async () => {
    const user = userEvent.setup();
    listTodos.mockResolvedValue([milk]);
    createTodo.mockResolvedValue({ id: 3, title: "çay al", completed: false });
    render(<App />);
    await screen.findByText("süt al");

    const input = screen.getByLabelText("Yeni görev");
    await user.type(input, "  çay al  ");
    await user.click(screen.getByRole("button", { name: "Ekle" }));

    await screen.findByText("çay al");
    expect(createTodo).toHaveBeenCalledWith("çay al");
    expect(screen.getAllByRole("checkbox")[0]).toHaveAccessibleName("çay al");
    expect(input).toHaveValue("");
  });

  it("boş görev için istek göndermez", async () => {
    const user = userEvent.setup();
    render(<App />);
    await screen.findByText("Henüz görev yok.");

    await user.type(screen.getByLabelText("Yeni görev"), "   ");
    await user.click(screen.getByRole("button", { name: "Ekle" }));

    expect(createTodo).not.toHaveBeenCalled();
  });

  it("ekleme başarısız olursa hatayı gösterir ve girişi korur", async () => {
    const user = userEvent.setup();
    createTodo.mockRejectedValue(new Error("İstek başarısız oldu (500)"));
    render(<App />);
    await screen.findByText("Henüz görev yok.");

    const input = screen.getByLabelText("Yeni görev");
    await user.type(input, "çay al");
    await user.click(screen.getByRole("button", { name: "Ekle" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("(500)");
    expect(input).toHaveValue("çay al");
  });

  it("onay kutusu tıklanınca görevi günceller", async () => {
    const user = userEvent.setup();
    listTodos.mockResolvedValue([milk]);
    updateTodo.mockResolvedValue({ ...milk, completed: true });
    render(<App />);

    await user.click(await screen.findByRole("checkbox", { name: "süt al" }));

    expect(updateTodo).toHaveBeenCalledWith(1, { completed: true });
    await waitFor(() =>
      expect(screen.getByRole("checkbox", { name: "süt al" })).toBeChecked(),
    );
  });

  it("Sil tıklanınca görevi listeden kaldırır", async () => {
    const user = userEvent.setup();
    listTodos.mockResolvedValue([milk]);
    deleteTodo.mockResolvedValue(null);
    render(<App />);
    await screen.findByText("süt al");

    await user.click(screen.getByRole("button", { name: "Sil" }));

    await waitFor(() =>
      expect(screen.queryByText("süt al")).not.toBeInTheDocument(),
    );
    expect(deleteTodo).toHaveBeenCalledWith(1);
  });

  it("silme başarısız olursa görevi listede tutar", async () => {
    const user = userEvent.setup();
    listTodos.mockResolvedValue([milk]);
    deleteTodo.mockRejectedValue(new Error("İstek başarısız oldu (500)"));
    render(<App />);
    await screen.findByText("süt al");

    await user.click(screen.getByRole("button", { name: "Sil" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("(500)");
    expect(screen.getByText("süt al")).toBeInTheDocument();
  });
});
