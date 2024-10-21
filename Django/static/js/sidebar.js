document.addEventListener('DOMContentLoaded', function () {
  const sidebar = document.getElementById('sidebar');
  const toggleButton = document.getElementById('toggle-sidebar');
  const sidebarIcon = document.getElementById('sidebar-icon');
  const mainContent = document.getElementById('main-content');

  // 페이지 로드 시 localStorage에서 상태를 불러오기
  const isCollapsed = localStorage.getItem('sidebar-collapsed');
  if (isCollapsed === 'true') {
    sidebar.classList.add('collapsed');
    mainContent.classList.add('expanded');
    sidebarIcon.classList.remove('fa-bars');
    sidebarIcon.classList.add('fa-chevron-right');
    // 사이드바 내용 숨기기
    sidebar.querySelector('.category-title').style.display = 'none'; // 추가
    sidebar.querySelector('.nav').style.display = 'none'; // 추가
  }

  // 버튼 클릭 시 사이드바 상태 토글 및 저장
  toggleButton.addEventListener('click', function () {
    sidebar.classList.toggle('collapsed');
    
    // 메인 컨텐츠 너비 조정
    if (sidebar.classList.contains('collapsed')) {
      mainContent.classList.add('expanded');
      sidebarIcon.classList.remove('fa-bars');
      sidebarIcon.classList.add('fa-chevron-right');
      localStorage.setItem('sidebar-collapsed', 'true'); // 상태 저장
      // 사이드바 내용 숨기기
      sidebar.querySelector('.category-title').style.display = 'none'; // 추가
      sidebar.querySelector('.nav').style.display = 'none'; // 추가
    } else {
      mainContent.classList.remove('expanded');
      sidebarIcon.classList.remove('fa-chevron-right');
      sidebarIcon.classList.add('fa-bars');
      localStorage.setItem('sidebar-collapsed', 'false'); // 상태 저장
      // 사이드바 내용 보이기
      sidebar.querySelector('.category-title').style.display = 'block'; // 추가
      sidebar.querySelector('.nav').style.display = 'block'; // 추가
    }
  });
});