class ScoreBoard extends AcGameObject {
    constructor(playground) {
        super();
        this.playground = playground;
        this.ctx = this.playground.game_map.ctx;
        this.$canvas = this.playground.game_map.$canvas;


        this.game_state = null; // 对局状态 win：胜利，lose：失败

        this.win_img = new Image();
        this.win_img.src = "https://cdn.acwing.com/media/article/image/2021/12/17/1_8f58341a5e-win.png";

        this.lose_img = new Image();
        this.lose_img.src = "https://cdn.acwing.com/media/article/image/2021/12/17/1_9254b5f95e-lose.png";
    }


    start() {
    }

    add_listening_events() {
        let outer = this;

        this.$canvas.on('click', function() {
            outer.playground.hide();
            outer.playground.root.menu.show();
        });
    }

    win() {
        this.game_state = "win";

        let outer = this;
        setTimeout(function() {
            outer.add_listening_events();
        }, 1000);
    }

    lose() {
        this.game_state = "lose";

        let outer = this;
        setTimeout(function() {
            outer.add_listening_events();
        }, 1000);
    }


    last_update() {
        this.render();
    }

    render() {
        let length = this.playground.height / 2;

        if (this.game_state === "win") {
            this.ctx.drawImage(this.win_img, this.playground.width / 2 - length / 2, this.playground.height / 2 - length / 2, length, length);
        } else if (this.game_state === "lose") {
            this.ctx.drawImage(this.lose_img, this.playground.width / 2 - length / 2, this.playground.height / 2 - length / 2, length, length);
        }
    }
}
