let allLanguageChars = "\\u0041-\\u005A\\u0061-\\u007A\\u00AA\\u00B5\\u00BA\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02C1\\u02C6-\\u02D1\\u02E0-\\u02E4\\u02EC\\u02EE\\u0370-\\u0374\\u0376\\u0377\\u037A-\\u037D\\u0386\\u0388-\\u038A\\u038C\\u038E-\\u03A1\\u03A3-\\u03F5\\u03F7-\\u0481\\u048A-\\u0527\\u0531-\\u0556\\u0559\\u0561-\\u0587\\u05D0-\\u05EA\\u05F0-\\u05F2\\u0620-\\u064A\\u066E\\u066F\\u0671-\\u06D3\\u06D5\\u06E5\\u06E6\\u06EE\\u06EF\\u06FA-\\u06FC\\u06FF\\u0710\\u0712-\\u072F\\u074D-\\u07A5\\u07B1\\u07CA-\\u07EA\\u07F4\\u07F5\\u07FA\\u0800-\\u0815\\u081A\\u0824\\u0828\\u0840-\\u0858\\u08A0\\u08A2-\\u08AC\\u0904-\\u0939\\u093D\\u0950\\u0958-\\u0961\\u0971-\\u0977\\u0979-\\u097F\\u0985-\\u098C\\u098F\\u0990\\u0993-\\u09A8\\u09AA-\\u09B0\\u09B2\\u09B6-\\u09B9\\u09BD\\u09CE\\u09DC\\u09DD\\u09DF-\\u09E1\\u09F0\\u09F1\\u0A05-\\u0A0A\\u0A0F\\u0A10\\u0A13-\\u0A28\\u0A2A-\\u0A30\\u0A32\\u0A33\\u0A35\\u0A36\\u0A38\\u0A39\\u0A59-\\u0A5C\\u0A5E\\u0A72-\\u0A74\\u0A85-\\u0A8D\\u0A8F-\\u0A91\\u0A93-\\u0AA8\\u0AAA-\\u0AB0\\u0AB2\\u0AB3\\u0AB5-\\u0AB9\\u0ABD\\u0AD0\\u0AE0\\u0AE1\\u0B05-\\u0B0C\\u0B0F\\u0B10\\u0B13-\\u0B28\\u0B2A-\\u0B30\\u0B32\\u0B33\\u0B35-\\u0B39\\u0B3D\\u0B5C\\u0B5D\\u0B5F-\\u0B61\\u0B71\\u0B83\\u0B85-\\u0B8A\\u0B8E-\\u0B90\\u0B92-\\u0B95\\u0B99\\u0B9A\\u0B9C\\u0B9E\\u0B9F\\u0BA3\\u0BA4\\u0BA8-\\u0BAA\\u0BAE-\\u0BB9\\u0BD0\\u0C05-\\u0C0C\\u0C0E-\\u0C10\\u0C12-\\u0C28\\u0C2A-\\u0C33\\u0C35-\\u0C39\\u0C3D\\u0C58\\u0C59\\u0C60\\u0C61\\u0C85-\\u0C8C\\u0C8E-\\u0C90\\u0C92-\\u0CA8\\u0CAA-\\u0CB3\\u0CB5-\\u0CB9\\u0CBD\\u0CDE\\u0CE0\\u0CE1\\u0CF1\\u0CF2\\u0D05-\\u0D0C\\u0D0E-\\u0D10\\u0D12-\\u0D3A\\u0D3D\\u0D4E\\u0D60\\u0D61\\u0D7A-\\u0D7F\\u0D85-\\u0D96\\u0D9A-\\u0DB1\\u0DB3-\\u0DBB\\u0DBD\\u0DC0-\\u0DC6\\u0E01-\\u0E30\\u0E32\\u0E33\\u0E40-\\u0E46\\u0E81\\u0E82\\u0E84\\u0E87\\u0E88\\u0E8A\\u0E8D\\u0E94-\\u0E97\\u0E99-\\u0E9F\\u0EA1-\\u0EA3\\u0EA5\\u0EA7\\u0EAA\\u0EAB\\u0EAD-\\u0EB0\\u0EB2\\u0EB3\\u0EBD\\u0EC0-\\u0EC4\\u0EC6\\u0EDC-\\u0EDF\\u0F00\\u0F40-\\u0F47\\u0F49-\\u0F6C\\u0F88-\\u0F8C\\u1000-\\u102A\\u103F\\u1050-\\u1055\\u105A-\\u105D\\u1061\\u1065\\u1066\\u106E-\\u1070\\u1075-\\u1081\\u108E\\u10A0-\\u10C5\\u10C7\\u10CD\\u10D0-\\u10FA\\u10FC-\\u1248\\u124A-\\u124D\\u1250-\\u1256\\u1258\\u125A-\\u125D\\u1260-\\u1288\\u128A-\\u128D\\u1290-\\u12B0\\u12B2-\\u12B5\\u12B8-\\u12BE\\u12C0\\u12C2-\\u12C5\\u12C8-\\u12D6\\u12D8-\\u1310\\u1312-\\u1315\\u1318-\\u135A\\u1380-\\u138F\\u13A0-\\u13F4\\u1401-\\u166C\\u166F-\\u167F\\u1681-\\u169A\\u16A0-\\u16EA\\u1700-\\u170C\\u170E-\\u1711\\u1720-\\u1731\\u1740-\\u1751\\u1760-\\u176C\\u176E-\\u1770\\u1780-\\u17B3\\u17D7\\u17DC\\u1820-\\u1877\\u1880-\\u18A8\\u18AA\\u18B0-\\u18F5\\u1900-\\u191C\\u1950-\\u196D\\u1970-\\u1974\\u1980-\\u19AB\\u19C1-\\u19C7\\u1A00-\\u1A16\\u1A20-\\u1A54\\u1AA7\\u1B05-\\u1B33\\u1B45-\\u1B4B\\u1B83-\\u1BA0\\u1BAE\\u1BAF\\u1BBA-\\u1BE5\\u1C00-\\u1C23\\u1C4D-\\u1C4F\\u1C5A-\\u1C7D\\u1CE9-\\u1CEC\\u1CEE-\\u1CF1\\u1CF5\\u1CF6\\u1D00-\\u1DBF\\u1E00-\\u1F15\\u1F18-\\u1F1D\\u1F20-\\u1F45\\u1F48-\\u1F4D\\u1F50-\\u1F57\\u1F59\\u1F5B\\u1F5D\\u1F5F-\\u1F7D\\u1F80-\\u1FB4\\u1FB6-\\u1FBC\\u1FBE\\u1FC2-\\u1FC4\\u1FC6-\\u1FCC\\u1FD0-\\u1FD3\\u1FD6-\\u1FDB\\u1FE0-\\u1FEC\\u1FF2-\\u1FF4\\u1FF6-\\u1FFC\\u2071\\u207F\\u2090-\\u209C\\u2102\\u2107\\u210A-\\u2113\\u2115\\u2119-\\u211D\\u2124\\u2126\\u2128\\u212A-\\u212D\\u212F-\\u2139\\u213C-\\u213F\\u2145-\\u2149\\u214E\\u2183\\u2184\\u2C00-\\u2C2E\\u2C30-\\u2C5E\\u2C60-\\u2CE4\\u2CEB-\\u2CEE\\u2CF2\\u2CF3\\u2D00-\\u2D25\\u2D27\\u2D2D\\u2D30-\\u2D67\\u2D6F\\u2D80-\\u2D96\\u2DA0-\\u2DA6\\u2DA8-\\u2DAE\\u2DB0-\\u2DB6\\u2DB8-\\u2DBE\\u2DC0-\\u2DC6\\u2DC8-\\u2DCE\\u2DD0-\\u2DD6\\u2DD8-\\u2DDE\\u2E2F\\u3005\\u3006\\u3031-\\u3035\\u303B\\u303C\\u3041-\\u3096\\u309D-\\u309F\\u30A1-\\u30FA\\u30FC-\\u30FF\\u3105-\\u312D\\u3131-\\u318E\\u31A0-\\u31BA\\u31F0-\\u31FF\\u3400-\\u4DB5\\u4E00-\\u9FCC\\uA000-\\uA48C\\uA4D0-\\uA4FD\\uA500-\\uA60C\\uA610-\\uA61F\\uA62A\\uA62B\\uA640-\\uA66E\\uA67F-\\uA697\\uA6A0-\\uA6E5\\uA717-\\uA71F\\uA722-\\uA788\\uA78B-\\uA78E\\uA790-\\uA793\\uA7A0-\\uA7AA\\uA7F8-\\uA801\\uA803-\\uA805\\uA807-\\uA80A\\uA80C-\\uA822\\uA840-\\uA873\\uA882-\\uA8B3\\uA8F2-\\uA8F7\\uA8FB\\uA90A-\\uA925\\uA930-\\uA946\\uA960-\\uA97C\\uA984-\\uA9B2\\uA9CF\\uAA00-\\uAA28\\uAA40-\\uAA42\\uAA44-\\uAA4B\\uAA60-\\uAA76\\uAA7A\\uAA80-\\uAAAF\\uAAB1\\uAAB5\\uAAB6\\uAAB9-\\uAABD\\uAAC0\\uAAC2\\uAADB-\\uAADD\\uAAE0-\\uAAEA\\uAAF2-\\uAAF4\\uAB01-\\uAB06\\uAB09-\\uAB0E\\uAB11-\\uAB16\\uAB20-\\uAB26\\uAB28-\\uAB2E\\uABC0-\\uABE2\\uAC00-\\uD7A3\\uD7B0-\\uD7C6\\uD7CB-\\uD7FB\\uF900-\\uFA6D\\uFA70-\\uFAD9\\uFB00-\\uFB06\\uFB13-\\uFB17\\uFB1D\\uFB1F-\\uFB28\\uFB2A-\\uFB36\\uFB38-\\uFB3C\\uFB3E\\uFB40\\uFB41\\uFB43\\uFB44\\uFB46-\\uFBB1\\uFBD3-\\uFD3D\\uFD50-\\uFD8F\\uFD92-\\uFDC7\\uFDF0-\\uFDFB\\uFE70-\\uFE74\\uFE76-\\uFEFC\\uFF21-\\uFF3A\\uFF41-\\uFF5A\\uFF66-\\uFFBE\\uFFC2-\\uFFC7\\uFFCA-\\uFFCF\\uFFD2-\\uFFD7\\uFFDA-\\uFFDC"

/**
 * consume content in one pair of parenthesis one time, return the remaining string
 * @param annotText
 * @param loc: how many siblings the current annotation root has(//todo: this could be wrong, should be the location of the node being processed now)
 * @param state
 * @param ht
 * @returns {*}
 */
function string2umr_recursive(annotText, loc, state, ht) {
    annotText = strip2(annotText);
    if (state === 'pre-open-parenthesis') {
        annotText = annotText.replace(/^[^(]*/, ""); // remove everything at the start point until the open parenthesis
        let pattern1 = `^\\(\\s*s[-_${allLanguageChars}0-9']*(\\s*\\/\\s*|\\s+)[${allLanguageChars}0-9][-_${allLanguageChars}0-9']*[\\s)]` // match something like (s1s / shadahast) or (s1s / shadahast with a newline at the end
        if (annotText.match(new RegExp(pattern1))) {
            annotText = annotText.replace(/^\(\s*/, ""); //remove left parenthesis
            let pattern2 = `^[${allLanguageChars}0-9][-_${allLanguageChars}0-9']*`
            let variableList = annotText.match(new RegExp(pattern2)); //match variable until the variable ends
            let pattern3 = `^[${allLanguageChars}0-9][-_${allLanguageChars}0-9']*\\s*`
            annotText = annotText.replace(new RegExp(pattern3), ""); //remove variable
            if (annotText.match(/^\//)) { // if annotText start with a forward slash /
                annotText = annotText.replace(/^\/\s*/, ""); //remove / and trailing space of /
            }
            let conceptList;
            let pattern4 = `^[:*]?[${allLanguageChars}0-9][-_${allLanguageChars}0-9']*[*]?`
            conceptList = annotText.match(new RegExp(pattern4)); //match the concept until the first concept ends
            annotText = annotText.replace(new RegExp(pattern4), ""); //remove the concept until the first concept ends

            let variable = variableList[0];
            let concept = conceptList[0];
            let new_variable;
            let new_concept;
            // THIS BLOCK ADD 1.c and RECORD CONCEPT
            let pattern5 = `^[${allLanguageChars}0-9][-_${allLanguageChars}0-9']*(?:-\\d+)?$`
            if (concept.match(new RegExp(pattern5)) //match something like quick-01
                || tolerate_special_concepts(concept)) { //todo
                umr[loc + '.c'] = concept;
                recordConcept(concept, loc);
                variable2concept[variable] = concept;
            } else { //todo
                new_concept = concept.toLowerCase();
                new_concept = new_concept.replace(/_/g, "-");
                new_concept = new_concept.replace(/-+/g, "-");
                new_concept = new_concept.replace(/-$/, "");
                if (new_concept.match(/^\d/)) {
                    new_concept = 'x-' + new_concept;
                }
                new_concept = new_concept.replace(/(\d)\D+$/, "$1");
                new_concept = new_concept.replace(/([a-z])(\d)/, "$1-$2");
                umr[loc + '.c'] = new_concept;
                recordConcept(new_concept, loc);
                variable2concept[variable] = new_concept;
            }
            // THIS BLOCK ADD 1.v AND RECORD VARIABLE
            if (getLocs(variable)) { // if variable already exists
                new_variable = newVar(concept);
                umr[loc + '.v'] = new_variable;
                recordVariable(new_variable, loc);
            } else if (variablesInUse[variable + '.conflict']) {
                umr[loc + '.v'] = variable;
                recordVariable(variable, loc);
            } else if (!variable.match(/^s\d*[a-z]\d*$/)) { // if variable doesn't match the shape of s1n1 (in the case of Chinese for example)
                new_variable = newVar(concept);
                umr[loc + '.v'] = new_variable;
                recordVariable(new_variable, loc);
            } else {
                umr[loc + '.v'] = variable;
                recordVariable(variable, loc);
            }
            umr[loc + '.s'] = '';
            umr[loc + '.n'] = 0;
            annotText = string2umr_recursive(annotText, loc, 'post-concept', ht);
            annotText = annotText.replace(/^[^)]*/, ""); // remove anything that is not ) at the start positions until ) appears
            annotText = annotText.replace(/^\)/, ""); // remove ) at the start position
        } else {
            if (umr[loc + '.r']) {
                var string_arg = 'MISSING-VALUE';
                umr[loc + '.s'] = string_arg;
                umr[loc + '.c'] = '';
                umr[loc + '.v'] = '';
                umr[loc + '.n'] = 0;
            } else {
                umr[loc + '.d'] = 1;
            }
            if (annotText.match(/^\(/)) { // )
                annotText = annotText.replace(/^\(/, ""); // )
                if (umr[loc + '.r']) {
                    annotText = string2umr_recursive(annotText, loc, 'post-concept', ht);
                } else {
                    annotText = string2umr_recursive(annotText, loc, 'pre-open-parenthesis', ht);
                }
            }
        }
    } else if (state === 'post-concept') {
        annotText = annotText.replace(/^[^:()]*/, ""); //remove anything that is not : ( ) until : ( ) appears
        let role_follows_p = annotText.match(/^:[a-z]/i);
        let open_para_follows_p = annotText.match(/^\(/);
        let role;
        if (role_follows_p || open_para_follows_p) {
            let n_children = umr[loc + '.n'];
            n_children++;
            umr[loc + '.n'] = n_children;
            let new_loc = loc + '.' + n_children;
            if (role_follows_p) {
                let roleList = annotText.match(/^:[a-z][-_a-z0-9]*/i); // match the role :actor
                annotText = annotText.replace(/^:[a-z][-_a-z0-9]*/i, ""); // remove the matched role from the rest of the annotText string
                role = roleList[0]; // :actor
            } else { //if there is no role follows parenthesis todo: don't allow to go here?
                role = ':mod'; // default
            }
            umr[new_loc + '.r'] = role;
            if (annotText.match(/^\s*\(/)) { // )
                annotText = string2umr_recursive(annotText, new_loc, 'pre-open-parenthesis', ht);
            } else {
                annotText = string2umr_recursive(annotText, new_loc, 'post-role', ht);
            }
            annotText = string2umr_recursive(annotText, loc, 'post-concept', ht);
        }
    } else if (state == 'post-role') { // expecting string, number, or variable
        if (annotText.match(/^\s/)) {
            annotText = annotText.replace(/^\s*/, "");
        } else {
            console.log("There is no space between role and post-role variable/string/concept");
        }
        let s_comp;
        let string_arg = '';
        let variable_arg = '';
        if (annotText.match(/^"/)) {
            annotText = annotText.replace(/^"/, "");
            var q_max_iter = 10;
            while ((q_max_iter >= 1) && !((annotText == '') || (annotText.match(/^"/)))) {
                if (s_comp = annotText.match(/^[^"\\]+/)) {
                    string_arg += s_comp[0];
                    annotText = annotText.replace(/^[^"\\]+/, "");
                }
                if (s_comp = annotText.match(/^\\./)) {
                    string_arg += s_comp[0];
                    annotText = annotText.replace(/^\\./, "");
                }
                q_max_iter--;
            }
            annotText = annotText.replace(/^"/, "");

        } else if (s_comp = annotText.match(/^:/)) {
            string_arg = 'MISSING-VALUE';
        } else if (s_comp = annotText.match(/^[^ ()]+/)) {
            string_arg = s_comp[0].replace(/\s*$/, "");
            annotText = annotText.replace(/^[^ ()]+/, "");
            if (getLocs(string_arg)) {
                variable_arg = string_arg;
                recordVariable(variable_arg, loc);
                string_arg = '';
            } else if (string_arg.match(/^[a-z]\d*$/)) {
                ht['provisional-string.' + loc] = string_arg;
            }
        } else {
            string_arg = 'MISSING-VALUE';
        }
        umr[loc + '.s'] = string_arg;
        umr[loc + '.c'] = '';
        umr[loc + '.v'] = variable_arg;
        var head_loc = loc.replace(/\.\d+$/, "");
        annotText = string2umr_recursive(annotText, head_loc, 'post-concept', ht);
    }
    return annotText;
}

/**
 * annotText got cut into pieces in this process, part of the annotText got cut off when it's got parsed successfully, and the leftover annotText string is the string to be parsed into umr
 * @param annotText : annotated string: (s1t / taste-01)
 * @returns {*}
 */
function string2umr(annotText) {
    let loc;
    let ps; //todo
    let ps_loc; //todo
    var ht = {}; //todo
    umr = {};
    umr['n'] = 0;
    variables = {};
    concepts = {};
    variablesInUse = {};
    let uncleanedRootVariables = annotText.match(/\(\s*s\d*[a-z]\d*[ \/]/g); // match each root vars (uncleaned): ["(s1t "]
    //populate variablesInUse
    uncleanedRootVariables.forEach(function(item, index){ // traverse each root
        let variable = item.replace(/^\(\s*/, ""); // get rid of the starting parenthesis: "s1t "
        variable = variable.replace(/[ \/]$/, ""); // get rid of the trailing space or /: "s1t"
        if (variablesInUse[variable]) {
            variablesInUse[variable + '.conflict'] = 1;
        } else {
            variablesInUse[variable] = 1;
        }
    });

    if (annotText.match(/\(/)) { //if there is an open parenthesis in annotText, e.g. annotText = "(s1t / taste-01)" meaning there is one node
        let prev_s_length = annotText.length; // 16
        let root_index = 1; // keep track of how many roots (how many graphs)
        loc = root_index + '';
        umr['n'] = 1;
        annotText = string2umr_recursive(annotText + ' ', loc, 'pre-open-parenthesis', ht);
        while (annotText.match(/^\s*[()]/) && (annotText.length < prev_s_length)) { // match ( ) regardless of space, and the annotText gets shorter
            root_index++;
            loc = root_index + '';
            prev_s_length = annotText.length;
            annotText = string2umr_recursive(annotText + ' ', loc, 'pre-open-parenthesis', ht);
            if (annotText.length < prev_s_length) {
                umr['n'] = umr['n'] + 1;
            }
        }
        for (var key in ht) { //todo: what is provisional-string
            console.log('investigating provisional-string ' + key + ' ' + ht[key]);
            if ((ps_loc = key.replace(/^provisional-string\.(\d+(?:\.\d+)*)$/, "$1"))
                && (ps = umr[ps_loc + '.s'])
                && getLocs(ps)
                && (ps == ht[key])) {
                // add_log('reframing provisional-string as variable ' + ps_loc + ' ' + ps + ' ' + ht[key]);
                umr[ps_loc + '.s'] = '';
                umr[ps_loc + '.v'] = ps;
                recordVariable(ps, ps_loc);
            }
        }
    } else {
        umr['n'] = 0;
    }
    variablesInUse = new Object();
    return strip(annotText);
}

/**
 * this is used to parse the penman string to umr
 * @param loaded_alignment
 * @param annotText
 */
function text2umr(annotText="", loaded_alignment='') {
    if (annotText && annotText!=="empty umr") { //annotText!=="empty umr" is because the older version saved <i>empty umr<i> in database sometimes
        string2umr(annotText); //populated umr

        //fill in the alignment information to umr
        if(loaded_alignment){
            let matches = loaded_alignment.match(/\((s\d*[a-z]\d*)\):\s((\d+-\d+)|undefined)/gm); //["(s1f): 4-4", "(s1t): 3-3"]
            if(matches){
                for(let i=0; i<matches.length; i++){
                    let variable = matches[i].replace(/\((s\d*[a-z]\d*)\):\s((\d+-\d+)|undefined)/gm, '$1');
                    let align_info = matches[i].replace(/\((s\d*[a-z]\d*)\):\s(\d+-\d+)/gm, '$2');
                    if(matches[i].includes("undefined")){
                        align_info = matches[i].replace(/\((s\d*[a-z]\d*)\):\sundefined/gm, '-1--1');
                    }
                    let loc = getLocs(variable);
                    umr[loc + '.a'] = align_info;
                }
            }
        }
    }
}