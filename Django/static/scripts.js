document.addEventListener('DOMContentLoaded', function () {
  // 대분류 클릭 시 중분류 토글
  const majorLinks = document.querySelectorAll('.major-category');

  majorLinks.forEach(link => {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      const middleList = this.nextElementSibling;
      if (middleList && middleList.tagName === 'UL') {
        middleList.style.display = middleList.style.display === 'none'
          ? 'block'
          : 'none';
      }
    });
  });

  // 중분류 클릭 시 하위분류 토글
  const middleLinks = document.querySelectorAll('.middle-category');
  middleLinks.forEach(link => {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      const subList = this.nextElementSibling;
      if (subList && subList.tagName === 'UL') {
        subList.style.display = subList.style.display === 'none'
          ? 'block'
          : 'none';
      }
    });
  });

  // 항목 클릭 시 입력창에 병명 전달
  const links = document.querySelectorAll('.major-category, .middle-category, .sub-category');

  links.forEach(link => {
    link.addEventListener('click', function (event) {
      event.preventDefault();

      // 병명만 가져오기 (코드 부분을 제외하고 가져오기)
      const nameParts = this
        .innerText
        .trim()
        .split('-'); // '-'로 분리
      const name = nameParts.length > 1
        ? nameParts[1].trim()
        : nameParts[0]; // 병명 부분 가져오기
      console.log(name); // 병명 확인

      const searchInput = document.getElementById('search-input');
      searchInput.value = name; // 검색창에 병명 입력
      this
        .closest('form')
        .submit(); // 폼 제출 (자동 검색)
    });
  });

  const rows = document.querySelectorAll('#result-body tr');

  rows.forEach(row => {
    row.addEventListener('click', function () {
      rows.forEach(r => r.classList.remove('selected'));
      this
        .classList
        .add('selected');

      const code = this.getAttribute('data-code');
      const name = this.getAttribute('data-name');
      const category = this.getAttribute('data-category');
      const details = this.getAttribute('data-details');

      const detailContent = document.getElementById('detail-content');

      // Split 'details' into buttons
      const detailsArray = details.split(' | ');
      let buttonsHTML = '';
      detailsArray.forEach(detail => {
        if (detail === '없음') {
            buttonsHTML += `<button class="btn btn-outline-secondary btn-sm detail-btn" type="button" disabled>${detail}</button> `;
        } else {
            buttonsHTML += `<button class="btn btn-outline-secondary btn-sm detail-btn" type="button" data-detail="${detail}">${detail}</button> `;
        }
      });

      

      // Update detail content
      detailContent.innerHTML = `
                  <p><strong>불완전 상병 코드:</strong> ${code}</p>
                  <p><strong>불완전 상병명:</strong> ${name}</p>
                  <p><strong>청구 카테고리:</strong> ${category}</p>
                  <p><strong>세부 청구 항목:</strong></p>
                  ${buttonsHTML}
              `;

      // Add click events to buttons (AJAX request)
      const detailButtons = document.querySelectorAll('.detail-btn');
      detailButtons.forEach(button => {
        button.addEventListener('click', function () {
          const detail = this.getAttribute('data-detail');

          // AJAX request
          fetch('/detail-action/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken') // CSRF 토큰을 헤더에 추가
            },
            body: JSON.stringify({detail: detail, code: code})
          })
            .then(response => response.json())
            .then(data => {
              if (data.link) {
                window.open(data.link, '_blank'); // 링크로 리다이렉트
              } else {
                alert('링크를 찾을 수 없습니다.');
              }
            })
            .catch(error => {
              console.error('Error:', error);
            });
        });
      });
    });
  });

  // "추가" 버튼 클릭 이벤트
  const addButton = document.getElementById('add-button');
  addButton.addEventListener('click', function (event) {
    event.preventDefault();
    // 여기에 추가 버튼 클릭 시의 행동을 정의하세요.
    alert('추가 버튼이 클릭되었습니다!');
    // 예를 들어, 추가 페이지로 이동:
    // window.location.href = "{% url 'add_view' %}";
  });
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document
      .cookie
      .split(';');
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