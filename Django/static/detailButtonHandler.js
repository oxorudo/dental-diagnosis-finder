document.addEventListener('DOMContentLoaded', (event) => {
  const resultBody = document.getElementById('result-body');

  // result-body에 클릭 이벤트 리스너 추가
  resultBody.addEventListener('click', (event) => {
    if (event.target.classList.contains('detail-btn')) {
      const button = event.target;
      const detail = button.getAttribute('data-detail');

      // 사용자에게 상세 정보를 볼 것인지 묻는 confirm 대화 상자
      const userConfirmation = window.confirm("상세 정보를 보시겠습니까?");

      if (userConfirmation) {
        // 사용자가 '예'를 클릭한 경우에만 서버 요청 실행
        fetch("/detail-action/", {  
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify({ detail: detail })
        })
        .then(response => response.json())
        .then(data => {
          if (data.link) {
            // 팝업 창으로 링크 열기
            window.open(data.link, '_blank');
          } else {
            alert('링크를 찾을 수 없습니다.');
          }
        })
        .catch(error => {
          console.error("Error:", error);
        });
      } else {
        // 사용자가 '아니오'를 클릭하면 아무것도 하지 않음
        alert('상세 정보를 보지 않았습니다.');
      }
    }
  });
});

// Utility function to get CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}