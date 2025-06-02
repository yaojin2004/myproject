// 轮播图
// 1. 初始数据
const data = [
    { url: url("{% static 'images/01.png' %}"), title: '对人类来说会不会有点太帅了？', color: 'rgb(100, 67, 68)' },
    { url: url("{% static 'images/02.png' %}"), title: '快看！是猴子', color: 'rgb(43, 35, 26)' },
    { url: url("{% static 'images/03.png' %}"), title: '光遇大雪谷！', color: 'rgb(36, 31, 33)' },
    { url: url("{% static 'images/04.png' %}"), title: '欧若拉：孩子们还不换等着哭吧', color: 'rgb(139, 98, 66)' },
    { url: url("{% static 'images/05.png' %}"), title: '快来分享你的时尚节穿搭吧~', color: 'rgb(67, 90, 92)' },
    { url: url("{% static 'images/06.png' %}"), title: '巫正：结婚证件照', color: 'rgb(166, 131, 143)' },
    { url: url("{% static 'images/07.png' %}"), title: '高级感杂志封面', color: 'rgb(53, 29, 25)' },
    { url: url("{% static 'images/08.png' %}"), title: '云朵甜甜圈谁敢尝', color: 'rgb(99, 72, 114)' },
]
// 获取元素
const img = document.querySelector('.slider-wrapper img')
const p = document.querySelector('.slider-footer p')
const footer = document.querySelector('.slider-footer')
// 1. 右按钮业务
// 1.1 获取右侧按钮 
const next = document.querySelector('.next')
let i = 0  // 信号量 控制播放图片张数
// 1.2 注册点击事件
next.addEventListener('click', function () {
    // console.log(11)
    i++
    i = i >= data.length ? 0 : i
    // 调用函数
    toggle()
})

// 2. 左侧按钮业务
// 2.1 获取左侧按钮 
const prev = document.querySelector('.prev')
// 1.2 注册点击事件
prev.addEventListener('click', function () {
    i--
    i = i < 0 ? data.length - 1 : i
    toggle()
})

// 声明一个渲染的函数作为复用
function toggle() {
    // 1.4 渲染对应的数据
    img.src = data[i].url
    p.innerHTML = data[i].title
    footer.style.backgroundColor = data[i].color
    // 1.5 更换小圆点    先移除原来的类名， 当前li再添加 这个 类名
    document.querySelector('.slider-indicator .active').classList.remove('active')
    document.querySelector(`.slider-indicator li:nth-child(${i + 1})`).classList.add('active')
}

// 3. 自动播放模块
let timerId = setInterval(function () {
    // 利用js自动调用点击事件  click()  一定加小括号调用函数
    next.click()
}, 1000)


// 4. 鼠标经过大盒子，停止定时器
const slider = document.querySelector('.slider')
// 注册事件
slider.addEventListener('mouseenter', function () {
    // 停止定时器
    clearInterval(timerId)
})

// 5. 鼠标离开大盒子，开启定时器
// 注册事件
slider.addEventListener('mouseleave', function () {
    // 停止定时器
    if (timerId) clearInterval(timerId)
    // 开启定时器
    timerId = setInterval(function () {
        // 利用js自动调用点击事件  click()  一定加小括号调用函数
        next.click()
    }, 1000)
})

function adjustContainerHeight() {
    const container = document.getElementById("background-container");
    container.style.height = `${container.scrollHeight}px`;
}

// 获取小圆点
const round_points = document.querySelectorAll('.slider-indicator li');
// 为每个li元素添加点击事件监听器
round_points.forEach((round_point, index) => {
    round_point.addEventListener('click', () => {
        // 移除所有li元素的active类
        round_points.forEach(li => li.classList.remove('active'));
        // 为当前点击的li元素添加active类
        round_point.classList.add('active');
        // 获取当前点击的li元素的索引
        i = Array.prototype.indexOf.call(round_points, round_point);
        toggle();
    });
});


// 在添加内容后调用
adjustContainerHeight();

document.addEventListener('DOMContentLoaded', function () {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const sortSelect = document.getElementById('sort-select');

    // 处理筛选按钮点击
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            // 移除其他按钮的active类
            filterBtns.forEach(b => b.classList.remove('active'));
            // 添加当前按钮的active类
            this.classList.add('active');

            // 获取筛选类型
            const type = this.dataset.type;
            // 获取当前排序方式
            const sort = sortSelect.value;

            // 更新URL参数
            updateUrlAndRefresh(type, sort);
        });
    });

    // 处理排序选择变化
    sortSelect.addEventListener('change', function () {
        // 获取当前筛选类型
        const activeFilter = document.querySelector('.filter-btn.active');
        const type = activeFilter ? activeFilter.dataset.type : 'all';
        // 获取新的排序方式
        const sort = this.value;

        // 更新URL参数
        updateUrlAndRefresh(type, sort);
    });

    // 更新URL参数并刷新页面
    function updateUrlAndRefresh(type, sort) {
        const url = new URL(window.location.href);

        // 更新URL参数
        if (type && type !== 'all') {
            url.searchParams.set('type', type);
        } else {
            url.searchParams.delete('type');
        }

        if (sort && sort !== 'latest') {
            url.searchParams.set('sort', sort);
        } else {
            url.searchParams.delete('sort');
        }

        // 保持分页参数
        const page = url.searchParams.get('page');
        if (!page || page === '1') {
            url.searchParams.delete('page');
        }

        // 更新URL并刷新页面
        window.location.href = url.toString();
    }
});