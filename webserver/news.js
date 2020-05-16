"use strict";
exports.__esModule = true;
var NewsAPI = require('newsapi');
var newsapi = new NewsAPI(process.env.NEWS_API_KEY);
function removeDuplicateArticles(articles) {
    var seen_urls = {};
    var new_articles = [];
    for (var _i = 0, articles_1 = articles; _i < articles_1.length; _i++) {
        var article = articles_1[_i];
        if (!(article.url in seen_urls)) {
            new_articles.push(article);
            seen_urls[article.url] = 1;
        }
    }
    return new_articles;
}
/* Recent Page - recent news about COVID-19 from the News API */
var recent_news = {};
var getNews = function (req, res) {
    var possible_categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'];
    var category = req.query['category'] || "general";
    if (!possible_categories.includes(category)) {
        category = "general";
    }
    /* 1000 ms/s * 60 s/m * 60 m/h * 1 h --> 1 hour cache age */
    var newsCacheExists = category in recent_news;
    if (newsCacheExists) {
        var newsCacheShouldBeUpdated = Date.now() - recent_news[category].update_time > 1000 * 60 * 360 * 1;
        if (!newsCacheShouldBeUpdated) {
            res.render("news", { articles: recent_news[category].articles });
            return;
        }
    }
    newsapi.v2.topHeadlines({
        q: 'coronavirus',
        language: 'en',
        country: 'us',
        category: category
    }).then(function (response) {
        recent_news[category] = {
            articles: removeDuplicateArticles(response.articles),
            update_time: Date.now()
        };
        res.render("news", { articles: recent_news[category].articles.slice(0, 10) });
    })["catch"](function (response) {
        console.log("There was an error during the News API! ", response);
        res.render("news", { articles: [] });
    });
};
exports.getNews = getNews;
