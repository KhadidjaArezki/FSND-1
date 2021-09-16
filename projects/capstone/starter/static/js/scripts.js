// import * as paginate from "./paginate.js";

let auth0 = null;
let user = null;
let user_id = null;
let token = null;
let isAuthenticated = false;
let login_button = document.getElementById('login');
let logout_button = document.getElementById('logout');
let myAlerts_button = document.getElementById('myAlerts');
let home_button = document.getElementById('home');
let userProfile = document.getElementById('user-profile');
let userAlerts = document.getElementById('user-alerts');
let recentAlerts = document.getElementById('recent-alerts');
let searchResults = document.getElementById('search-results');
// let searchButton = document.getElementById("button-search");

window.onload = async () => {
  getFilters();
  await configureClient();
  await processLoginState();
  login_button.onclick = login;
  logout_button.onclick = logout;
//   searchButton.onclick = getSearchResults;
  updateUI();
};

const fetchAuthConfig = () => fetch("/auth_config");

const configureClient = async () => {
  console.log('Inside configureClient');
  const response = await fetchAuthConfig();
  const config = await response.json();
  auth0 = await createAuth0Client({
    domain: config.domain,
    client_id: config.client_id,
    audience: config.audience,
    redirectUri: config.redirectUri,
    scope: config.scope
  })
};

const processLoginState = async () => {
  console.log('processLoginState');
  // Check code and state parameters in auth0 response url
  const query = window.location.search;
  console.log('query: ' + query);
  if (query.includes("code=") && query.includes("state=")) {
    // Process the login state
    await auth0.handleRedirectCallback();
    // Use replaceState to redirect the user away and remove the querystring parameters
    window.history.replaceState({}, 
      document.title, 
      window.location.pathname
    );
  }
};

const updateUI = async () => {
  console.log('Inside updateUI');
  isAuthenticated = await auth0.isAuthenticated();
  // NEW - add logic to show/hide gated content after authentication
  if (isAuthenticated) {

    // Show logout and my alerts buttons
    login_button.classList.add('hidden');
    logout_button.classList.remove('hidden');
    myAlerts_button.classList.remove('hidden');
    userProfile.classList.remove('hidden');

    // Get and store user auth0 data
    token = await auth0.getTokenSilently();
    // $("#ipt-access-token").html(token);
    window.localStorage.setItem('jwt', token);
    user = JSON.stringify(await auth0.getUser());
    // $("#ipt-user-profile").html(user);
    window.localStorage.setItem('user', user);
    user = JSON.parse(user);
    user_id = user['sub'].substring(
        user['sub'].indexOf('|') + 1, 
        user['sub'].length
    );
    
    // if user is the manager, greet 
    if (user['nickname'] === 'jimaimaharimna' ) {
        greetManager();
    }
    if (user['nickname'] === 'khadidjaarezki999') {
        greetAdmin();
    }
    // Show profile name, picture and myAlerts
    showUserData(user);
    // Send user profile and get recent alerts
    identifyUser(user);
    // Set event handler on my alerts button
    myAlerts_button.onclick =  getMyAlerts;
  } 
  else {
    logout_button.classList.add('hidden');
    login_button.classList.remove('hidden');
    myAlerts_button.classList.add('hidden');

  }
};

const getMyAlerts = () => {
    document.querySelector(".pagination").innerHTML = '';
    const data = {}
    getItems(1, 'user-alerts', data);
    showDelEditButtons();
    let myAlertsLink = document.querySelector("li#myAlerts>a.nav-link");
    handleNavBar(myAlertsLink, myAlerts_button);
};

const showDelEditButtons = () => {
    if (isAuthenticated) {
        var checkEdit = setInterval(function() {
            const editButtons = document.querySelectorAll('button.edit-alert');
            if (editButtons.length) {
                for (let i = 0; i < editButtons.length; i++) {
                    editButtons[i].classList.remove('hidden');
                    editButtons[i].onclick = editAlert;
                }
                clearInterval(checkEdit);
            }
        }, 100);
        var checkDel = setInterval(function() {
            const delButtons = document.querySelectorAll('button.del-alert');
            console.log(delButtons);
            if (delButtons.length) {
                for (let i = 0; i < delButtons.length; i++) {
                    delButtons[i].classList.remove('hidden');
                    delButtons[i].onclick = delAlert;
                }
                clearInterval(checkDel);
            }
        }, 100);
    }
};

const editAlert = (event) => {
    const alertId = event.target.closest('.card').dataset['id'];
    var popup = document.getElementById("edit-popup");
    popup.classList.add("show");
    const editAlertForm = document.querySelector('#edit-popup form');
    editAlertForm.onsubmit = function() {
        // Get product data from result box of the button that triggered the call
        const desiredPrice = $('#edit-alert-box').val(); 
        const alertData = {
            'user_id': user_id,
            'new_desired_price': desiredPrice,
            'alert_id': alertId
        };   
        const request = new Request('/alerts', {
            method: 'PATCH',
            body: JSON.stringify(alertData),
            headers: {'Content-Type': 'application/json'}
        });
        fetch(request)
        .then(response => response.json())
        .then(jsonResponse => {
            console.log(jsonResponse);
            console.assert(true, jsonResponse['success']);
            popup.classList.remove("show");
            getMyAlerts();
        })
        .catch(function(e) {
            console.error(e.message);
        });
    }; 
};

const delAlert = (event) => {
    const alertId = event.target.closest('.card').dataset['id'];
    console.log(alertId);
    const request = new Request('/alerts', {
        method: 'DELETE',
        body: JSON.stringify({
            'alert_id': alertId,
            'user_id': user_id
        }),
        headers: {'Content-Type': 'application/json'}
    });
    fetch(request)
    .then(response => response.json())
    .then(jsonResponse => {
        console.log(jsonResponse);
        console.assert(true, jsonResponse['success']);
        getMyAlerts();
    })
    .catch(function(e) {
        console.error(e.message);
    });
};

const login = async () => {
  login_button.onclick =  function (event){
    event.preventDefault();
  };
  await auth0.loginWithRedirect({
    redirect_uri: window.location.href,
  });
};

const identifyUser = (user) => {
    // send user to '/user'
    var request = new Request('/user', {
        method: 'POST',
        body: JSON.stringify({
            'user_id': user_id,
            'email': user['email'],
            'user_name': user['nickname'],
        }),
        headers: {'Content-Type': 'application/json'}
    });
    fetch(request)
    .then(response => response.json())
    .then(jsonResponse => {
        console.assert(true, jsonResponse['success']);
        // Get user's recent alerts
        document.querySelector(".pagination").innerHTML = '';
        const data = {};
        getItems(1, 'recent-alerts', data);
        showDelEditButtons();
    })
    .catch(function(e) {
        console.error(e.message);
    });
};

const logout = () => {
  window.localStorage.removeItem('jwt');
  window.localStorage.removeItem('user');
  auth0.logout({
    returnTo: window.location.href,
  });
};

const showUserData = (user) => {
  let userName = user['nickname'];
  let userImg = user['picture'];
  document.querySelector('img.user-img').src = userImg;
  document.getElementById('user-name').innerHTML+= userName;
};

const getItems = (page, itemType, data) => {
  showLoading('#items-container');
  console.log(data);
  console.log('Inside getItems: page= '+page+' itemType= '+itemType);
  let itemContainers = document.getElementById('items-container').children;
  handleContainerVisibility(itemContainers, itemType);
  let endPoint = mapItemType(itemType);
  data['page_number'] = page;
  data['user_id'] = user_id;
  let request = formRequest(endPoint, data);
  
  fetch(request)
  .then(response => response.json())
  .then(jsonResponse => {
    console.log(jsonResponse);
    showItems(jsonResponse, itemType, page, data);
    hideLoading();
  })
  .catch(function(e) {
    console.error(e.message);
  }); 
};

const handleContainerVisibility = (itemContainers, itemType) => {
    recentAlerts.classList.remove("current");
    userAlerts.classList.remove("current");
    searchResults.classList.remove("current");
    recentAlerts.innerHTML = '';
    userAlerts.innerHTML = '';
    searchResults.innerHTML = '';
};

const formRequest = (endPoint, data) => {
  let url = '/' + endPoint;
  var request = new Request(url, {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {'Content-Type': 'application/json'}
  });
  return request  
};

const mapItemType = (itemType) => {
  let itemTypeMapper = {
    'recent-alerts': 'recent_alerts',
    'user-alerts': 'alerts',
    'search-results': 'search'
  };
  let endPoint = itemTypeMapper[itemType];
  return endPoint;
};

const getSearchResults = () => {
    const data = getSearchData();
    let homeLink = document.querySelector("li#home>a.nav-link");
    handleNavBar(homeLink, home_button);
    document.querySelector(".pagination").innerHTML = '';
    getItems(1, 'search-results', data);
    showAddAlertButtons();
};

const getSearchData = () => {
    const keywords = $('#search-box').val();
    let filters = {};
    const location = $('#location-input').val();
    filters['location'] = location === 'Select...'? '' : location;
    const category = $('#category-input').val();
    filters['categoryId'] = category === 'Select...'? '' : category;
    const store = $('#store-input').val();
    filters['store'] = store === 'Select...'? '' : store;
    const price_value = $('#price-input').val();
    const price = price_value === 'Select...'? '': price_value;
    const minPrice = price.substring(0, price.indexOf('-'));
    const maxPrice = price.substring(price.indexOf('-')+1, price.length);
    filters['min_price'] = minPrice;
    filters['max_price'] = maxPrice;

    const data = {
        'keywords': keywords,
        'filters': filters
    };
    return data;
};

const showAddAlertButtons = async() => {
    if(isAuthenticated) {
        var checkExist = setInterval(function() {
            const addAlertButtons = document.querySelectorAll('#search-results button');
            if (addAlertButtons.length) {
               for (let i = 0; i < addAlertButtons.length; i++) {
                    addAlertButtons[i].classList.remove("hidden");
                    addAlertButtons[i].onclick = addAlert;
                }
                clearInterval(checkExist);
            }
         }, 100);
    }
};

const addAlert = (event) => {
    var popup = document.getElementById("add-popup");
    popup.classList.add("show");
    const productBox = event.target.parentNode;
    const productData = getProductData(productBox);
    const addAlertForm = document.querySelector('#add-popup form');
    addAlertForm.onsubmit = function() {
        // Get product data from result box of the button that triggered the call
        const desiredPrice = $('#add-alert-box').val();    
        productData['desired_price'] = desiredPrice;
        productData['user_id'] = user_id;
        const request = new Request('/alerts/add', {
            method: 'POST',
            body: JSON.stringify(productData),
            headers: {'Content-Type': 'application/json'}
        });
        fetch(request)
        .then(response => response.json())
        .then(jsonResponse => {
            console.log(jsonResponse);
            console.assert(true, jsonResponse['success']);
            popup.classList.remove("show");
        })
        .catch(function(e) {
            console.error(e.message);
        });
    };
};

const getProductData = (productBox) => {
    const productId = productBox.dataset['id'];
    const productImage = productBox.getElementsByTagName('img')[0].src;
    const productName = productBox.querySelector('h6>a').innerHTML;
    const productLink = productBox.querySelector('.result-product>h6>a').href;
    const priceTag = productBox.querySelector('.result-product>h6').nextSibling.innerHTML;
    const productPrice = priceTag.substring(priceTag.indexOf(' ') +1, priceTag.length);
    const productStore = productBox.querySelector('.text-muted').innerHTML;
    const productData = {
        'product_id': productId,
        'product_image': productImage,
        'product_name': productName,
        'product_link': productLink,
        'product_price': productPrice,
        'product_store': productStore
    };
    console.log(productData);
    return productData;

};

const showItems = (jsonResponse, itemType, page, data) => {
    const itemsBox = document.getElementById(itemType);
    itemsBox.classList.add("current")
    let totalItems = jsonResponse['total_items'];
    let items = jsonResponse[itemType];
    if (items.length === 0) {
        let emptyMessage = '';
        if (itemType === 'search-results') emptyMessage = '<p>No results matched your search</p>';
        else  emptyMessage = '<p>Your alerts will appear here</p>';
        itemsBox.innerHTML = emptyMessage;
    }
    else {
        let title = '';
        let itemClass = '';
        if (itemType === 'search-results') {
            title = '<h4>Search Results</h4>';
            itemClass = 'result';
        }
        else if (itemType === 'recent-alerts') {
            title = '<h4>My Recent Alerts</h4>';
            itemClass = 'alert';
        }
        else {
            title = '<h4>My Alerts</h4>';
            itemClass = 'alert';
        }
        itemsBox.innerHTML = title;

        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            let item_div = '';
            if (itemType === 'search-results') {
                item_div+= '<div class="card item" data-id= "' + item['product_id'] + '">';
                item_div+= '<button class="btn btn-primary hidden" type="button">Add Alert</button>';
            }
            else {
                item_div+= '<div class="card item" data-id= "' + item['alert_id'] + '">';
            }
            item_div+= '<div class="cart-body">';
            item_div+= '<div class="' + itemClass +'-img">';
            item_div+= '<img class="card-img-top" src="' + item['product_image'] + '">';
            item_div+= '<div class="small text-muted">' + item['product_store'] + '</div></div>';
            item_div+= '<div class="' + itemClass +'-product">';
            item_div+= '<h6 class="card-title"><a href="' + item['product_link'] + '">' + item['product_name'] + '</a></h6>';
            item_div+= '<div>Price: ' + item['product_currency'] + ' ' + item['product_price'] + '</div>';
            if (itemType !== 'search-results') {
                item_div+= '<div>Difference in price: ' + item['price_difference'] + '</div>';
                item_div+= '<div>Desired price: ' + item['desired_price'] + '</div>';
                item_div+= '<span><button class="btn btn-primary edit-alert hidden" type="button">Edit</button>';
                item_div+= '<button class="btn btn-primary del-alert hidden" type="button">Delete</button></span>';
            }
            item_div+= '</div></div><hr>';
            itemsBox.innerHTML+= item_div;
        }
        console.log('########################### Total Items: ' + totalItems);
        if (totalItems <= 5) {
            $('#pagination').hide();
        }
        else {
            $('#pagination').show();
            // $('#paginable').hide();
            paginateResponse(totalItems, page, data);
        }
    }
};

const getFilters = () => {
    fetch('/filters')
    .then(response => response.json())
    .then(jsonResponse => {
        console.log(jsonResponse);
        console.assert(true, jsonResponse['success']);
        showFilters(jsonResponse);
    })
    .catch(function(e) {
        console.error(e.message);
    });
};

const showFilters = (jsonResponse) => {
    const filters = jsonResponse['filters'];
    // Show hidden filters in search-form
    for (let i = 0; i < filters.length; i++) {
        const filter = filters[i];
        document.getElementById(filter).classList.remove("hidden");
    }
    const allFilters = document.querySelectorAll("#add-filter option");
    const inputGroups = document.querySelectorAll('#search-filters>div.input-group');
    for (let i = 0; i < inputGroups.length; i++) {
        const inputGroup = inputGroups[i];
        if (!inputGroup.classList.contains("hidden")) {
            const inputGroupId = inputGroup.id;
            // get option element inside filters with value == input_group_id
            const filterToRemove = [].filter.call(allFilters, function(optionElement) {
                return optionElement.value.indexOf(inputGroupId) > -1;
            })[0];
            console.log(filterToRemove);
            // remove this option
            document.getElementById('filter-input').removeChild(filterToRemove);
        }
    }
};

const greetManager = () => {
    document.getElementById('add-filter').classList.remove("hidden");
    var addFilterForm = document.querySelector('#add-filter .needs-validation');
    addFilterForm.onsubmit = addFilter;
};

const addFilter = () => {
    const filter = $('#filter-input').val();
    if (filter !== 'Select...') {
        // const filterToAdd = document.getElementById(filter);
        // filterToAdd.classList.remove("hidden");
        const request = new Request('/filters', {
            method: 'POST',
            body: JSON.stringify({'filter': filter}),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            }
        });
        fetch(request)
        .then(response => response.json())
        .then(jsonResponse => {
            console.assert(jsonResponse['success'], true);
            location.reload();
        })
        .catch(function(e) {
            console.error(e.message);
        });
    }
};

const greetAdmin = () => {
    greetManager();
    document.getElementById('add-deal').classList.remove("hidden");
    var addDealForm = document.querySelector('#add-deal .needs-validation');
    addDealForm.onsubmit = addDeal;
};

const addDeal = async() => {
    const dealName = $('#deal-name').val();
    const dealLink = $('#deal-link').val();
    const dealImage = $('#deal-image').val();
    const dealPrice = $('#deal-price').val();
    const dealCurrency = $('#deal-currency').val();
    const dealStore = $('#deal-store').val();

    const request = new Request('/deals',{
        method: 'POST',
        body: JSON.stringify({
            'deal_name': dealName,
            'deal_link': dealLink,
            'deal_image': dealImage,
            'deal_price': dealPrice,
            'deal_currency': dealCurrency,
            'deal_store': dealStore 
        }),
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }
    });
    fetch(request)
    .then(response => response.json())
    .then(jsonResponse => {
        console.assert(jsonResponse['success'], true);
        location.reload();
    })
    .catch(function(e) {
        console.error(e.message);
    });
};

const handleNavBar = (navItem, button) => {
  // let currentActives = $('li.nav-item>a:active');
  let currentActives = document.querySelectorAll('li.nav-item>a.active');
  navItem.classList.add("active");
  for (let i = 0; i < currentActives.length; i++) {
    currentActives[i].classList.remove("active");
  }
//   button.onclick = function (event){
//     event.preventDefault();
//   };
};

// Show loading icon inside element identified by 'selector'.
const showLoading = (selector) => {
  $('#loading').show();
};

const hideLoading = () => {
  $('#loading').hide();
};

////////////////////////////////////////////////////////////////////////
// Code snippet from https://getbootstrap.com/docs/5.1/forms/validation/

// Example starter JavaScript for disabling form submissions if there are invalid fields
(function () {
    'use strict'
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.querySelectorAll('.needs-validation');
    var searchForm = document.querySelector('#search-form .needs-validation')
  
    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
      .forEach(function (form) {
        form.addEventListener('submit', function (event) {
          if (!form.checkValidity()) {
            console.log('invalid form');
            event.preventDefault()
            event.stopPropagation()
          }
          else {
            console.log('search submitted');
            event.preventDefault();
          }
          form.classList.add('was-validated')
        }, false)
      });
    searchForm.onsubmit = getSearchResults;
})()

// const domain = 'fs-webdev.eu.auth0.com';
// const audience = 'price_tracker';
// const clientID = 'qfecxJQCicccSMa1KSVM8I6VP85NrYHV';
// const callbackURL = 'http://localhost:5000/';
// const scope = 'openid%20profile%20email';
// {"nickname":"jimaimaharimna","name":"jimaimaharimna@gmail.com","picture":"https://s.gravatar.com/avatar/dbd032730a0fe9189070ee6e8cefc989?s=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fji.png","updated_at":"2021-09-04T01:43:20.307Z","email":"jimaimaharimna@gmail.com","email_verified":false,"sub":"auth0|6130edff4fb5980069cfe064"}


///////////////////////////////////////////////////////////////////////
// PAGINATION MODULE

// Code source: https://codepen.io/kshoeb/pen/NQboaL

// Returns an array of maxLength (or less) page numbers
// where a 0 in the returned array denotes a gap in the series.
// Parameters:
//   totalPages:     total number of pages
//   page:           current page
//   maxLength:      maximum size of returned array
const getPageList = (totalPages, page, maxLength)  => {
  console.log('Inside getPageList, totalPages= ' + totalPages + ' currentPage= ' +page);
  if (maxLength < 5) throw "maxLength must be at least 5";

  function range(start, end) {
    return Array.from(Array(end - start + 1), (_, i) => i + start);
  }

  var sideWidth = maxLength < 9 ? 1 : 2;
  var leftWidth = (maxLength - sideWidth * 2 - 3) >> 1;
  var rightWidth = (maxLength - sideWidth * 2 - 2) >> 1;
  if (totalPages <= maxLength) {
    // no breaks in list
    return range(1, totalPages);
  }
  if (page <= maxLength - sideWidth - 1 - rightWidth) {
    // no break on left of page
    return range(1, maxLength - sideWidth - 1)
      .concat([0])
      .concat(range(totalPages - sideWidth + 1, totalPages));
  }
  if (page >= totalPages - sideWidth - 1 - rightWidth) {
    // no break on right of page
    return range(1, sideWidth)
      .concat([0])
      .concat(
        range(totalPages - sideWidth - 1 - rightWidth - leftWidth, totalPages)
      );
  }
  // Breaks on both sides
  return range(1, sideWidth)
    .concat([0])
    .concat(range(page - leftWidth, page + rightWidth))
    .concat([0])
    .concat(range(totalPages - sideWidth + 1, totalPages));
};

const  paginateResponse = (numberOfItems, page, data) => {
  console.log(data);
  console.log('Inside paginateResponse, numberOfItems= ' + numberOfItems);
  var limitPerPage = 5;
  // Total pages rounded upwards
  var totalPages = Math.ceil(numberOfItems / limitPerPage);
  // Number of buttons at the top, not counting prev/next,
  // but including the dotted buttons.
  // Must be at least 5:
  var paginationSize = 5;
  var currentPage;

  const showPage = (whichPage) =>  {
    if (whichPage <= 1 ) whichPage = 1;
    if (whichPage >= totalPages) whichPage = totalPages;
    console.log('Inside showPage: page= '+whichPage);
      
    currentPage = whichPage;
    $("#paginable").show();
      // .hide()
      // .slice((currentPage - 1) * limitPerPage, currentPage * limitPerPage)
      // .show();
    // Replace the navigation items (not prev/next):
    $(".pagination li").slice(1, -1).remove();
    getPageList(totalPages, currentPage, paginationSize).forEach(item => {
      $("<li>")
        .addClass(
          "page-item " +
            (item ? "current-page " : "") +
            (item === currentPage ? "active " : "")
        )
        .append(
          $("<a>")
            .addClass("page-link")
            .on('click', function() {
              if (item) {
                console.log('Inside pagination button: page= '+item);
                let page = parseInt(item);
                let itemTypeDiv = $('#paginable>div').filter(".current").first();
                let itemType = itemTypeDiv.attr('id');
                getItems(page, itemType, data);
                showAddAlertButtons();
              }
            })
            .text(item || "...")
        )
        .insertBefore("#next-page");
    });
    // return true;
  };

  // Include the prev/next buttons:
  $(".pagination").append(
    $("<li>").addClass("page-item").attr({ id: "previous-page" }).append(
      $("<a>")
        .addClass("page-link")
        .on('click', function() {
          let page =  $('.pagination li.active>a.page-link').text();
          page = parseInt(page) - 1;
          if (page <= 0) page = 1;
          console.log('Inside previous button: page= '+ page);
          let itemTypeDiv = $('#paginable>div').filter(".current").first();
          let itemType = itemTypeDiv.attr('id');
          getItems(page, itemType, data);
          showAddAlertButtons();
        })
        .text("Prev")
    ),
    $("<li>").addClass("page-item").attr({ id: "next-page" }).append(
      $("<a>")
        .addClass("page-link")
        .on('click', function() {
          let page = $('.pagination li.active>a.page-link').text();
          page = parseInt(page) + 1;
          if (page >= totalPages) page = totalPages;
          console.log('Inside next button: page= '+ page);
          let itemTypeDiv = $('#paginable>div').filter(".current").first();
          let itemType = itemTypeDiv.attr('id');
          getItems(page, itemType, data);
          showAddAlertButtons();
        })
        .text("Next")
    )
  );
  // Show the page links
  $("#paginable").show();
  showPage(page);

  $(".pagination").on("click", function() {
    $("html,body").animate({ scrollTop: 350 }, 0);
  });
};
