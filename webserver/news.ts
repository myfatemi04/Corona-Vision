const NewsAPI = require('newsapi');
const newsapi = new NewsAPI(process.env.NEWS_API_KEY);

function removeDuplicateArticles(articles) {
    let seen_urls = {};
    let new_articles = [];
    for (let article of articles) {
        if (!(article.url in seen_urls)) {
            new_articles.push(article);
            seen_urls[article.url] = 1;
        }
    }
    return new_articles;
}

/* Recent Page - recent news about COVID-19 from the News API */
let recent_news = {};
let getNews = (req, res) => {
    let possible_categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'];
    let category = req.query['category'] as string || "general";
    if (!possible_categories.includes(category)) {
        category = "general";
    }

    /* 1000 ms/s * 60 s/m * 60 m/h * 1 h --> 1 hour cache age */
    let newsCacheExists = category in recent_news;
    if (newsCacheExists) {
        let newsCacheShouldBeUpdated = Date.now() - recent_news[category].update_time > 1000 * 60 * 360 * 1;
        if (!newsCacheShouldBeUpdated) {
            res.render("news", {articles: recent_news[category].articles});
            return;
        }
    }
    
    newsapi.v2.topHeadlines({
        q: 'coronavirus',
        language: 'en',
        country: 'us',
        category: category
    }).then(
        response => {
            recent_news[category] = {
                articles: removeDuplicateArticles(response.articles),
                update_time: Date.now()
            }
            res.render("news", {articles: recent_news[category].articles.slice(0, 10)});
        }
    ).catch(
        response => {
            console.log("There was an error during the News API! ", response);
            res.render("news", {articles: []});
        }
    );
};

export {
    getNews
};
