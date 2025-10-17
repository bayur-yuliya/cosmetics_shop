function openDeleteDialog(id, name) {
  document.getElementById("deleteText").textContent = `Удалить товар ${name}?`;
  document.getElementById("deleteId").value = id;
  document.getElementById("deleteDialog").showModal();
}