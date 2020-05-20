function confirmModal(obj){
    $('#hidden_input').val(obj.id);
    $("#confirm-modal").show();
}

function closeModal() {
    $("#confirm-modal").modal('hide');
}

function zoomOut() {
    $("#zoom-modal").modal('hide');
}

function zoomModal(obj) {
  document.getElementById("img").src = obj.src;
  $('#zoom-modal').show();
}