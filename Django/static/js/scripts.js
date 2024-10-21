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
      const nameParts = this.innerText.trim().split('-'); // '-'로 분리
      const name = nameParts.length > 1 ? nameParts[1].trim() : nameParts[0]; // 병명 부분 가져오기
      console.log(name); // 병명 확인
  
      const searchInput = document.getElementById('search-input');
      searchInput.value = name; // 검색창에 병명 입력
  
      const form = document.getElementById('search-form'); // 폼을 명확히 선택 (폼에 ID가 있다고 가정)
      if (form) {
        form.submit(); // 폼 제출 (자동 검색)
      } else {
        console.error("Form not found!");
      }
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
      if (detailContent) {
        detailContent.innerHTML = `
            <p><strong>불완전 상병 코드:</strong> ${code}</p>
            <p><strong>불완전 상병명:</strong> ${name}</p>
            <p><strong>청구 카테고리:</strong> ${category}</p>
            <p><strong>세부 청구 항목:</strong></p>
            ${buttonsHTML}
        `;
      } else {
          console.error("Element with id 'detail-content' not found");
      }
    });
  });

  // // "추가" 버튼 클릭 이벤트
  // const addButton = document.getElementById('add-button');
  // addButton.addEventListener('click', function (event) {
  //   event.preventDefault();
  //   // 여기에 추가 버튼 클릭 시의 행동을 정의하세요.
  //   alert('추가 버튼이 클릭되었습니다!');
  //   // 예를 들어, 추가 페이지로 이동:
  //   // window.location.href = "{% url 'add_view' %}";
  // });

  // AJAX 요청을 통해 검색 결과 가져오기
  const searchForm = document.querySelector('form');
  searchForm.addEventListener('submit', function (event) {
    event.preventDefault(); // 기본 폼 제출 방지
    const query = document.getElementById('search-input').value;

    fetch(`?q=${encodeURIComponent(query)}`, {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest' // AJAX 요청임을 서버에 알림
      }
    })
    .then(response => response.json())
    .then(data => {
      // 검색 결과 처리
      const resultBody = document.getElementById('result-body');
      if (resultBody) { // resultBody가 null이 아닌지 확인
        resultBody.innerHTML = ''; // 기존 결과 초기화

        if (data.results.length > 0) {
          data.results.forEach(row => {
            const tr = document.createElement('tr');
            tr.setAttribute('data-code', row.code);
            tr.setAttribute('data-name', row.name);
            tr.setAttribute('data-category', row.categories.map(c => c.name).join(', '));
            tr.setAttribute('data-details', row.split_details.join(' | '));
            tr.innerHTML = `
              <td class="col-code">${row.code}</td>
              <td class="col-name">${row.name}</td>
              <td class="col-category">
                ${row.categories.map(category => `<button class="btn btn-sm category-btn" type="button" style="background-color: ${category.color}; color: white;" disabled>${category.name}</button>`).join('')}
              </td>
              <td class="col-details">
                ${row.split_details.map(detail => `<button class="btn btn-sm btn-outline-secondary detail-btn" type="button" data-detail="${detail}">${detail}</button>`).join('')}
              </td>
            `;
            resultBody.appendChild(tr);
          });
        } else {
          resultBody.innerHTML = '<tr><td colspan="4" class="text-center">검색 결과가 없습니다.</td></tr>';
        }
      } else {
        console.error("Element with id 'result-body' not found");
      }
    })
    .catch(error => console.error('Error fetching search results:', error));
  });
});

