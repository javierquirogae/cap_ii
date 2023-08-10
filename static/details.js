'use strict';

const KEY = 'apiKey=f513086da55b4ffbbb711aa83cdddd70';
const RECIPE_URL = 'https://api.spoonacular.com/recipes';

const $res_area = $("#res");
const $detail = $('h2');


async function getRecipeDetails(id) {
    let ingredients_list = [];
    const response = await axios.get(
        `${RECIPE_URL}/${id}/information?${KEY}`
        );    
    ingredients_list = response.data.extendedIngredients;
    console.log(response.data);
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


getRecipeDetails($detail.attr("id"));