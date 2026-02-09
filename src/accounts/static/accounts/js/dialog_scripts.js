function openDeleteDialog() {
  document.getElementById("deleteText").textContent = `Удалить аккаунт?`;
  document.getElementById("deleteDialog").showModal();
}

function openLogoutDialog() {
    document.getElementById("logoutText").textContent = `Выйти из аккаунта?`;
    document.getElementById("logoutDialog").showModal();
}