$('.js-click-modal').click(function () {
  var container = $(this).closest('.container');
  container.addClass('modal-open');
  container.siblings('.container').addClass('modal-hidden');
});

$('.js-close-modal').click(function () {
  var container = $(this).closest('.container');
  container.removeClass('modal-open');
  $('.container').removeClass('modal-hidden');
});
