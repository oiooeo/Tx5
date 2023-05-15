$('.js-click-modal').click(function () {
  var container = $(this).closest('.container');
  container.addClass('modal-open');
  container.siblings().fadeOut(300); // 애니메이션 속도 조정
});

$('.js-close-modal').click(function () {
  var container = $(this).closest('.container');
  container.removeClass('modal-open');
  setTimeout(function () {
    container.siblings().fadeIn(300); // 애니메이션 속도 조정
  }, 500); // 딜레이 시간 조정
});
