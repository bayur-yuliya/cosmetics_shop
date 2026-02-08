function openDeleteDialog(id, name) {
  document.getElementById("deleteText").textContent = `Удалить товар ${name}?`;
  document.getElementById("deleteForm").action = `${window.location.pathname}delete/${id}/`;
  document.getElementById("deleteDialog").showModal();
}