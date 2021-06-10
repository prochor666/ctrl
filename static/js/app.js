"use strict";

class LocalStorage
{
    constructor()
    {
        this.site = 'ctrl';
    }

    compose(key)
    {
        return [this.site, key].join('/');
    };

    test(key)
    {
        return this.compose(key);
    };

    get(key)
    {
        return localStorage.getItem(this.compose(key));
    };

    set(key, value)
    {
        return localStorage.setItem(this.compose(key), value);
    };

    remove(key)
    {
        return localStorage.removeItem(this.compose(key));
    };
};

window.lst = new LocalStorage;

class Auth
{
    login(key)
    {

    };

    logged(key)
    {

    };
}
