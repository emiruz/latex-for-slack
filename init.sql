create table if not exists tokens(team_id primary key not null,
       	     	    	          user_id not null,
				  bot_token not null,
				  created not null);
