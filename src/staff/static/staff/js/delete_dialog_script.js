function openDeleteDialog(id, name) {
  document.getElementById("deleteText").textContent = `Удалить товар ${name}?`;
  document.getElementById("deleteForm").action = `${window.location.pathname}${id}/delete/`;
  document.getElementById("deleteDialog").showModal();
}