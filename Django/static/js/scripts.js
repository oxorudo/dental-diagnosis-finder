document.addEventListener('DOMContentLoaded', function () {
  // 대분류 및 중분류 클릭 시 토글 기능
  const toggleList = (link) => {
    const list = link.nextElementSibling;
    if (list && list.tagName === 'UL') {
      list.style.display = list.style.display === 'none' ? 'block' : 'none';
    }
  };

  const majorLinks = document.querySelectorAll('.major-category');
  majorLinks.forEach(link => {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      // 더블 클릭이면 토글 안 함
      if (event.detail === 1) { // 클릭이 단일 클릭인 경우만
        toggleList(this);
      }
    });

    link.addEventListener('dblclick', function (event) {
      event.preventDefault();
      handleDoubleClick(this); // 더블 클릭 핸들러 호출
    });
  });

  const middleLinks = document.querySelectorAll('.middle-category');
  middleLinks.forEach(link => {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      // 더블 클릭이면 토글 안 함
      if (event.detail === 1) {
        toggleList(this);
      }
    });

    link.addEventListener('dblclick', function (event) {
      event.preventDefault();
      handleDoubleClick(this); // 더블 클릭 핸들러 호출
    });
  });

  // 항목 클릭 시 입력창에 코드 전달 및 검색
  const links = document.querySelectorAll('.major-category, .middle-category, .sub-category');
  links.forEach(link => {
    link.addEventListener('click', function (event) {
      event.preventDefault();
      setSearchInputAndSubmit(this);
    });
  });

  // 더블 클릭 핸들러 함수
  function setSearchInputAndSubmit(link) {
    // 코드만 가져오기 (병명 부분을 제외하고 가져오기)
    const nameParts = link.innerText.trim().split('-'); // '-'로 분리
    const name = nameParts.length > 1 ? nameParts[0].trim() : nameParts[0]; // 코드 부분 가져오기

    // 코드 뒤에 ~가 있으면 제거
    const cleanedName = name.replace(/\s*~\s*$/, '');
    console.log(cleanedName); // 코드 확인

    const searchInput = document.getElementById('search-input');
    searchInput.value = cleanedName; // 검색창에 코드 입력

    const searchButton = document.querySelector('.search-btn'); // 클래스로 검색 버튼 선택
    if (searchButton) {
      searchButton.click(); // 버튼 클릭
    } else {
      console.error("Search button not found!");
    }
  }

  // 검색 결과 업데이트
  const rows = document.querySelectorAll('#result-body tr');
  rows.forEach(row => {
    row.addEventListener('click', function () {
      rows.forEach(r => r.classList.remove('selected'));
      this.classList.add('selected');

      const code = this.getAttribute('data-code');
      const name = this.getAttribute('data-name');
      const category = this.getAttribute('data-category');
      const details = this.getAttribute('data-details');

      const detailContent = document.getElementById('detail-content');

      // Split 'details' into buttons
      const detailsArray = details.split(' | ');
      let buttonsHTML = '';
      detailsArray.forEach(detail => {
        buttonsHTML += detail === '없음'
          ? `<button class="btn btn-outline-secondary btn-sm detail-btn" type="button" disabled>${detail}</button>`
          : `<button class="btn btn-outline-secondary btn-sm detail-btn" type="button" data-detail="${detail}">${detail}</button>`;
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

  // "추가" 버튼 클릭 이벤트
  const addButton = document.getElementById('add-button');
  addButton.addEventListener('click', function (event) {
    event.preventDefault();
    alert('추가 버튼이 클릭되었습니다!');
  });

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
        const resultBody = document.getElementById('result-body');
        if (resultBody) {
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
