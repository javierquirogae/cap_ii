'use strict';

const KEY = 'apiKey=f513086da55b4ffbbb711aa83cdddd70';
const RECIPE_URL = 'https://api.spoonacular.com/recipes';

const $res_area = $("#res");
const $GO_button = $("#GO");
const $search_form = $("#search_form");
const $rand_sug = $("#rand_sug");
const $save_area = $("#save_div");
const $liked_recipes = $("#liked_recipe_list");
const $plan = $("#plan");
// calss="add_ons"
const $add_ons_l = $(".add_ons_l");
const $add_ons_m = $(".add_ons_m");



$res_area.on("click", function (evt) {
    evt.preventDefault();
    let target = evt.target;
    console.log(target.id);
    getRecipeDetails(target.id);
});



async function getRecipeDetails(id) {
    let ingredients_list = [];
    const response = await axios.get(
        `${RECIPE_URL}/${id}/information?${KEY}`
    );
    $save_area.empty();

    const payloadSt = `${id}/${encodeURIComponent(response.data.title)}`;

    $save_area.append(` <form method="POST" action="/save_recipe/${payloadSt}">
                            <button class="btn btn-outline-success">
                                add to favorites
                            </button>
                        </form>`);
    $save_area.append(` <form method="POST" action="/add_to_plan/${payloadSt}">
                            <button class="btn btn-outline-info" id="${id}">
                                add to meal plan
                            </button>
                        </form>`);
    ingredients_list = response.data.extendedIngredients;

    $res_area.empty();
    $res_area.append(`<div>`);
    $res_area.append(`<h2>${response.data.title}</h2>`);

    $res_area.append(`</div>`);
    $res_area.append(`<p> </p>`);
    $res_area.append(`<p><b>CATEGORIES</b> : ${response.data.cuisines}</p>`);
    $res_area.append(`<p><b>SUITABLE FOR</b> : ${response.data.dishTypes}</p>`);
    $res_area.append(`<p><b>DIETS</b> : ${response.data.diets}</p>`);
    $res_area.append(`<p><b>READY IN</b> : ${response.data.readyInMinutes} minutes</p>`);
    $res_area.append(`<p><b>MAKES</b> : ${response.data.servings} servings</p>`);

    $res_area.append(`<img src="${response.data.image}">`);
    $res_area.append(`<p> </p>`);

    $res_area.append(`<h3>DIRECTIONS : </h3>`);
    $res_area.append(`<p>${response.data.instructions}</p>`);
    $res_area.append(`<br>`);

    $res_area.append(`<h3>INGREDIENTS : </h3>`);
    $res_area.append(`<ul>`);
    for (let i = 0; i < ingredients_list.length; i++) {
        $res_area.append(`<li>${ingredients_list[i].original}</li>`);
    }
    $res_area.append(`</ul>`);

    $res_area.append(`<a href="${response.data.sourceUrl}" target="_blank">Visit source</a>`);


}


$GO_button.on("click", function (event) {
    event.preventDefault();
    $save_area.empty();
    $res_area.empty();
    let search_term = $('#search_form input[name="search_term"]').val();
    console.log(search_term);
    getRecipe(search_term);
});



async function getRecipe(query, l = 100) {
    let loop_legth = 0;
    let id_array = [];
    let length = `number=${l}`;
    let q = `query=${query}`;

    const response = await axios.get(
        `${RECIPE_URL}/complexSearch?${KEY}&${q}&${length}`
    );

    if (response.data.number > response.data.totalResults) {
        loop_legth = response.data.totalResults;
    } else {
        loop_legth = response.data.number;
    }

    for (let i = 0; i < loop_legth; i++) {
        console.log(response.data.results[i].title);
        $res_area.append(`<p
                            class="link"
                            id="${response.data.results[i].id}">
                            ${response.data.results[i].title}</p>`);
        console.log(response.data.results[i].id);
        id_array.push(response.data.results[i].id);
    }
    return id_array;
}


async function getRnadRecipe() {
    const response = await axios.get(
        `${RECIPE_URL}/random?${KEY}&number=1`
    );
    $rand_sug.append(`<p
                        class="link"
                        id="${response.data.recipes[0].id}">
                        May I suggest you try, 
                        ${response.data.recipes[0].title}</p>`);
}



$rand_sug.on("click", function (evt) {
    evt.preventDefault();
    let target = evt.target;
    console.log(target.id);
    getRecipeDetails(target.id);
});

async function populateFavorites() {
    await $add_ons_l.each(async function () {
        $(this).append(`<a href="/saved_recipe_detail/${$(this).attr('id')}">
                            View
                        </a>`);
    });
}

async function populatePlan() {
    await $add_ons_m.each(async function () {
        $(this).append(`<a href="/saved_recipe_detail/${$(this).attr('id')}">
                            View
                        </a>`);
    });
    await $add_ons_m.each(async function () {
        addMealToPlan($(this).attr('id'));
    });
}


async function addMealToPlan(id) {
    let ingredients_list = [];
    let title = '';
    // check if meal is already in plan
    try {
        const response = await axios.get(
            `${RECIPE_URL}/${id}/information?${KEY}`
        );
        const res = await axios.get(`/get_meal_ingredients/${id}`);

        title = response.data.title;
        ingredients_list = response.data.extendedIngredients;
        console.log(`Meal id : ${id} `);
        console.log(`Meal title : ${title} `);
        console.log(`ingredient lenght : ${ingredients_list.length}`)
        console.log(`saved ingredient lenght : ${res.data.length}`)
        if (ingredients_list.length == res.data.length) {
            console.log(`Meal ${id} already in plan`);
            return;
        }
       
        console.log(ingredients_list);
        await Promise.all(ingredients_list.map(async ingredient => {
           
            console.log(`Adding recipe ${title} to meal plan`);
            console.log(`Adding ingredient ${ingredient.nameClean} to meal ${id}`);
            const payload = {
                meal_id: id,
                ingredient_id: ingredient.id,
                name: ingredient.nameClean,
                aisle: ingredient.aisle,
                amount_us: ingredient.measures.us.amount,
                unit_us: ingredient.unit,
            };

            try {
                const response = await axios.post('/add_ingredient', payload);
                console.log(`Ingredient ${ingredient.nameClean} added. Response:`, response.data);
            } catch (error) {
                console.error(`Error adding ingredient ${ingredient.nameClean} with id ${ingredient.id}:`, error);
                // Handle errors
            }
        }));
    } catch (error) {
        console.error(`Error fetching recipe data for meal ${id}:`, error);
        // Handle errors
    }
}




$('a').on("click", function (evt) {
    let target = evt.target;
    console.log(target.id);
    window.location.href = `/saved_recipe_detail/${target.id}`;
});


populateFavorites();
populatePlan()
getRnadRecipe();