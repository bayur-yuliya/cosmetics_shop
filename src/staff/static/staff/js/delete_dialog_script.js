function openDeleteDialog(button) {
  const id = button.dataset.id;
  const name = button.dataset.name;

  document.getElementById("deleteText").textContent =
    `Удалить товар ${name}?`;

  document.getElementById("deleteForm").action =
    `${window.location.pathname}${id}/delete/`;

  document.getElementById("deleteDialog").showModal();
}