var App = {
    submit_data : function(obj, submit_obj, url, callback, loader_id) {
	$("#message___all__").hide();
        App.show_loader("Submitting", loader_id);
        for(var i in obj["value"]){
            $("#message_"+ obj["value"][i]).html("");
            $("#container_"+ obj["value"][i]).removeClass("error");
            submit_obj[obj["value"][i]] = $("#id_" + obj["value"][i]).val();
        }
        for(var j in obj["check"]){
            if($("#id_"+obj["check"][j]).is(':checked')){
                submit_obj[obj["check"][j]] = "True";//$("#id_"+obj["check"][j]).attr('value');
            }else{
                submit_obj[obj["check"][j]] = "False";//obj["check"][j]["unchecked_value"];
            }
        }
        for(var k in obj["check_group"]){
            var check_group = document.getElementsByName(obj["check_group"][k]);
            var added_counter = 0;
            for(cg_counter=0;cg_counter<check_group.length; cg_counter++){
                if($(check_group[cg_counter]).is(':checked')){
                    if(added_counter === 0){
                        submit_obj[obj["check_group"][k]+"_alias"] = $(check_group[cg_counter]).attr('value')+",";
                    }else{
                        submit_obj[obj["check_group"][k]+"_alias"] = submit_obj[obj["check_group"][k]+"_alias"]+$(check_group[cg_counter]).attr('value')+",";
                    }
                    added_counter++;
                }
            }
        }
        submit_obj["csrfmiddlewaretoken"] = $('input[name="csrfmiddlewaretoken"]')[0].value;
	$.post(url, submit_obj, function(data){
            App.hide_loader(loader_id);
            App.process_data(data, callback);
        }).error(function(xhr){
	    App.hide_loader(loader_id);
	    App.handle_ajax_error(xhr);
	});
    },
    handle_ajax_error:function(xhr){
	switch (xhr.status){
	    case 404:
	    App.show_error("Requested function not found");
	    break;
	    case 403:
	    App.show_error("You don't have access to perform this action");
	    break;
	    case 500:
	    App.show_error("A system error has occured.");
	    break;
	    default:
	    App.show_error("Error!!!");
	};

    },
    submit_data_iframe:function(form, obj, loader_id){
	$("#message___all__").hide();
	App.hide_error();
	App.hide_info();
	App.hide_warning();
        App.show_loader("Submitting", loader_id);
	for(var i in obj["value"]){
            $("#message_"+ obj["value"][i]).html("");
            $("#container_"+ obj["value"][i]).removeClass("error");
        }
        for(var j in obj["check"]){
            $("#message_"+ obj["value"][i]).html("");
            $("#container_"+ obj["value"][i]).removeClass("error");
        }
	$("#"+form).submit();
    },

    process_data : function(data_str, callback){
        data = JSON.parse(data_str);
        switch (data["code"]){
        case "form_error":
            App.process_error(data["errors"]);
            App.show_error(App.code_message[data["code"]]);
            break;
        case "system_error":
            App.show_error(App.code_message[data["code"]]);
            break;
        case "callback":
            callback(data);
            break;
        case "invalid_request":
            App.show_error(App.code_message[data["code"]]);
            callback(data);
            break;
        case "registered":
            window.location.href = data["success_page"];
            break;
        case "login":
            callback(data);
            break;
        case "data_loaded":
            callback(data);
            break;
	case "server_message":
            App.show_info(App.code_message[data["server_message"]]);
            break;
        default:
            alert("unknown response");
        }
    },
    code_message:{"access_denied" : "You don't have access for this operation",
        "form_error" : "The data submitted is not valid. Please make sure you have entered correct data",
        "system_error" : "A system error has occured. Please contact the site administrator",
        "invalid_request" : "In valid request"
        },

    process_error:function(errors){
        for (var i in errors){
            var error_message = "";
            for (var j in errors[i]){
                if(j>0){
                    error_message+="<br/>";
                }
                error_message += errors[i][j];
            }
            $("#message_" + i).html(error_message);
            $("#container_" + i).addClass("error");
        }
        if ("__all__" in errors){
            $("#message___all__").show();
        }
    },
    clear_form:function(ids){
        for (var i in ids){
            $("#id_"+ids[i]).attr('value','');
        }
    },
    populate_form:function(dict){
        for (var key in dict){
            $("#id_" + key).val(dict[key]);
        }
    },
    currentLoader:0,
    currentLoaderId:"null",
    show_loader:function(loader_id, message){
	i = 0;
	App.currentLoaderId = loader_id;
	App.currentLoader = setInterval(function() {
	    i = ++i % 10;
	    $("#"+loader_id).html(message+Array(i+1).join("."));
	}, 500);
	
    },
    hide_loader:function(){
	clearInterval(App.currentLoader);
	$("#"+App.currentLoaderId).html($("#"+App.currentLoaderId).data('text'));
    },
    showButtonLoader:function(loader_id, message){
	$("#"+loader_id).addClass('disabled');
	App.showLoader(loader_id, message);
    },
    hideButtonLoader:function(){
	$("#"+App.currentLoaderId).removeClass('disabled');
	App.hideLoader();
    },
    submitForm:function(e){
	App.showButtonLoader(e.target.id, "Submitting");
    },
    show_info:function(info_message){
        $("#info").html(info_message);
        $("#info").slideDown();
        setTimeout("App.hide_info()",3000);
    },
    hide_info:function(){
        $("#info").slideUp("slow");
        //$("#info").html("");
    },
    show_error:function(info_message){
        $("#error").html(info_message);
        $("#error").slideDown();
        setTimeout("App.hide_error()",5000);
    },
    hide_error:function(){
        $("#error").slideUp("slow");
        //$("#info").html("");
    },
    show_warning:function(info_message){
        $("#warning").html(info_message);
        $("#warning").slideDown();
        setTimeout("App.hide_warning()",3000);
    },
    hide_warning:function(){
        $("#warning").slideUp("slow");
        //$("#info").html("");
    },
    User:{
	save_user:function(){
            var obj = {"value":["user_id", "username", "password1", "password2", "email"]};
            App.submit_data(obj,{},"/add/user", App.User.save_user_callback, "loader");
	},
	save_user_callback:function(data){
            $("#id_user_id").val(data["user_id"]);
	},
	login:function(){
            var obj = {"value":["username", "password"],"check":["remember_me"]};
            App.submit_data(obj,{},"/login_user", App.User.login_callback, "loader");
	},
	login_callback:function(data){
            window.location.href = data["next_view"];
	},
	password_reset_email:function(){
	    var obj = {"value":["email"]};
            App.submit_data(obj,{},"/password/reset/submit/email", App.User.password_reset_email_callback, "loader");
	},
	password_reset_email_callback:function(data){
	    $("#email_form").hide();
	    $("#email_sent").show();
	},
	password_reset_password:function(data){
	    var obj = {"value":["password","confirm_password"]};
            App.submit_data(obj,{},"/password/reset/submit/password", App.User.password_reset_password_callback, "loader");
	},
	password_reset_password_callback:function(data){
	    location.href=data["redirect"];
	}
	
    }
    
};

