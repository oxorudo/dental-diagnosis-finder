document.addEventListener('DOMContentLoaded', function () {
  // 대분류 및 중분류 클릭 시 토글 기능
  const toggleList = (link) => {
      const list = link.nextElementSibling;
      if (list && list.tagName === 'UL') {
          list.style.display = list.style.display === 'none' ? 'block' : 'none';
      }
  };

  const majorLinks = document.querySelectorAll('.major-category');
  const middleLinks = document.querySelectorAll('.middle-category');
  const subLinks = document.querySelectorAll('.sub-category'); // 하위 분류 추가

  [...majorLinks, ...middleLinks, ...subLinks].forEach(link => {
      link.addEventListener('click', function (event) {
          event.preventDefault();
          // 단일 클릭 시 토글
          if (event.detail === 1) {
              toggleList(this); 
          }
      });

      link.addEventListener('dblclick', function (event) {
          event.preventDefault();
          handleDoubleClick(this); // 더블 클릭 시 검색 버튼 클릭
      });
  });

  // 더블 클릭 시 입력창에 코드 전달 후 검색 버튼 클릭
  function handleDoubleClick(link) {
      setSearchInputAndSubmit(link);
  }

  // 검색창에 코드 입력 후 검색 버튼 클릭
  function setSearchInputAndSubmit(link) {
      // 코드만 가져오기 (병명 부분을 제외하고 가져오기)
      const nameParts = link.innerText.trim().split('-'); // '-'로 분리
      const name = nameParts.length > 1 ? nameParts[0].trim() : nameParts[0]; // 코드 부분 가져오기

      // 코드 뒤에 ~가 있으면 제거
      const cleanedName = name.replace(/\s*~\s*$/, '');
      console.log(cleanedName); // 코드 확인

      const searchInput = document.getElementById('search-input');
      searchInput.value = cleanedName; // 검색창에 코드 입력

      const searchButton = document.querySelector('.search-btn'); // 검색 버튼 찾기
      if (searchButton) {
          searchButton.click(); // 더블 클릭 시 검색 버튼 클릭
      } else {
          console.error("Search button not found!");
      }
  }

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
          if (resultBody) {
              resultBody.innerHTML = ''; // 기존 결과 초기화

              if (data.results.length > 0) {
                  data.results.forEach((row, index) => { // 인덱스 추가
                      const tr = document.createElement('tr');
                      tr.setAttribute('data-code', row.code);
                      tr.setAttribute('data-name', row.name);

                      // 카테고리가 있으면 표시, 없으면 공백
                      const categoriesHTML = row.categories.length > 0 ? 
                          row.categories.map(category => 
                              `<button class="btn btn-sm category-btn" type="button" style="background-color: ${category.color}; color: white;" disabled>${category.name}</button>`
                          ).join('') : 'N/A';

                      // 세부 청구 항목이 있으면 표시, 없으면 공백
                      const detailsHTML = row.split_details.length > 0 ? 
                          row.split_details.map(detail => 
                              `<button class="btn btn-sm btn-outline-secondary detail-btn" type="button" data-detail="${detail}">${detail}</button>`
                          ).join('') : 'N/A';

                      tr.innerHTML = `
                          <td class="col-index">${index + 1}</td> <!-- 인덱스 추가 -->
                          <td class="col-code">${row.code}</td>
                          <td class="col-name">${row.name}</td>
                          <td class="col-category">${categoriesHTML}</td>
                          <td class="col-details">${detailsHTML}</td>
                      `;
                      resultBody.appendChild(tr);
                  });
              } else {
                  resultBody.innerHTML = '<tr><td colspan="5" class="text-center">검색 결과가 없습니다.</td></tr>'; // 열 수 조정
              }
          } else {
              console.error("Element with id 'result-body' not found");
          }
      })
      .catch(error => console.error('Error fetching search results:', error));
  });
});
