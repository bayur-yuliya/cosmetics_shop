function openDeleteDialog(id, name) {
  document.getElementById("deleteText").textContent = `Удалить товар ${name}?`;
  document.getElementById("deleteDialog").showModal();
}