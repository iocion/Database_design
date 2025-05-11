const { createApp } = Vue;

const app = createApp({
    data() {
        return {
            books: [
                { title: "Old Man's War" },
                { title: "The Lock Artist" },
                { title: "HTML5" },
                { title: "Right Ho Jeeves" },
                { title: "The Code of the Wooster" },
                { title: "Thank You Jeeves" }
            ]
        };
    }
});

app.component('v-select', vSelect);
console.log("VueSelect:", vSelect); // 检查 VueSelect 是否定义
app.mount('#app');