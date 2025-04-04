from pathlib import Path

from sqlalchemy import and_,distinct
from flask import render_template, url_for, flash, redirect, request, Blueprint, Response, current_app, session, jsonify, make_response
from flask_login import login_user, current_user, logout_user, login_required
from umr_annot_tool import db, bcrypt
from umr_annot_tool.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, SearchUmrForm, UpdateProjectForm
from umr_annot_tool.models import User, Post, Doc, Annotation, Sent, Projectuser, Project, Docqc, Docda, Lattice, Lexicon, Partialgraph
from umr_annot_tool.users.utils import save_picture, send_reset_email
from sqlalchemy.orm.attributes import flag_modified
import logging
import json
import re
from sqlalchemy.sql import expression
from one_time_scripts.parse_input_xml import html
from lemminflect import getLemma


users = Blueprint('users', __name__)

@users.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')


        # filepath = Path(__file__).parent.parent.joinpath("static/sample_files/news-text-2-lorelei.txt")
        # with open(filepath, 'r', encoding='utf-8') as f:
        #     content_string = f.read()
        # filename = 'news-text-2-lorelei.txt'
        # file_format = 'plain_text'
        # lang = 'english'
        # info2display = html(content_string, file_format, lang)
        # doc = Doc(lang=lang, filename=filename, content=content_string, user_id=user.id,
        #           file_format=file_format)
        # db.session.add(doc)
        # db.session.commit()
        # flash('Your doc has been created!', 'success')
        # for sent_of_tokens in info2display.sents:
        #     sent = Sent(content=" ".join(sent_of_tokens), doc_id=doc.id)
        #     db.session.add(sent)
        #     db.session.commit()
        # flash('Your sents has been created.', 'success')

        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.account'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('users.account'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    return redirect(url_for('main.display_post'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'POST':
        try:
            to_delete_project_id = int(request.form["delete_project"])
            print("to_delete_project_id: ", to_delete_project_id)
            if to_delete_project_id !=0:
                Partialgraph.query.filter(Partialgraph.project_id==to_delete_project_id).delete()
                print("Partialgraph removed")
                Lattice.query.filter(Lattice.project_id==to_delete_project_id).delete()
                print("Lattice removed")
                Lexicon.query.filter(Lexicon.project_id == to_delete_project_id).delete()
                print("Lexicon removed")
                Docda.query.filter(Docda.project_id==to_delete_project_id).delete()
                print("Docda removed")
                Docqc.query.filter(Docqc.project_id==to_delete_project_id).delete()
                print("Docqc removed")
                qc_id = Project.query.filter(Project.id==to_delete_project_id).first().qc_user_id
                Projectuser.query.filter(Projectuser.project_id == to_delete_project_id).delete()
                print("Projectuser removed")
                Project.query.filter(Project.id==to_delete_project_id).delete()
                print("Project removed")
                to_delete_doc_ids = Doc.query.filter(Doc.project_id == to_delete_project_id).all()
                for to_delete_doc in to_delete_doc_ids:
                    Annotation.query.filter(Annotation.doc_id == to_delete_doc.id).delete()
                    Sent.query.filter(Sent.doc_id == to_delete_doc.id).delete()
                    Doc.query.filter(Doc.id == to_delete_doc.id).delete()
                User.query.filter(User.id == qc_id).delete()
            db.session.commit()
        except Exception as e:
            flash("deleting doc from database failed", 'info')
            print(e)
            print("deleting doc from database failed")
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    projects = Projectuser.query.filter(Projectuser.user_id == current_user.id).all()
    historyDocs = Doc.query.filter(Doc.user_id == current_user.id).all()
    belongToProject=[]
    for hds in historyDocs:
        belongToProject.append(Project.query.get_or_404(hds.project_id).project_name)
    # print("belongToProject: ", belongToProject)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form, historyDocs=historyDocs,
                           projects=projects, belongToProject=belongToProject)

@login_required
@users.route("/project/<int:project_id>", methods=['GET', 'POST'])
def project(project_id):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    form = UpdateProjectForm()
    project_name = Project.query.filter(Project.id == project_id).first().project_name

    if form.validate_on_submit():
        print("I am here 33")
        p = Project.query.filter(Project.id==project_id).first()
        p.project_name = form.projectname.data
        flag_modified(p, 'project_name')
        pus = Projectuser.query.filter(Projectuser.project_id==project_id).all()
        for pu in pus:
            pu.project_name = form.projectname.data
            flag_modified(pu, 'project_name')
        db.session.commit()
        flash('Project name has been updated!', 'success')
        return redirect(url_for('users.project', project_id=project_id))
    elif request.method == 'POST':
        try:
            new_member_name = request.form["new_member_name"]
            print("new_member_name", new_member_name)
            update_doc_id = int(request.form["update_doc_id"]) #delete from project
            print("update_doc_id:", update_doc_id)
            remove_member_id = int(request.form["remove_member_id"])
            print("remove_member_id", remove_member_id)
            annotated_doc_id = int(request.form["annotated_doc_id"])
            print("annotated_doc_id:", annotated_doc_id)
            delete_annot_doc_id = int(request.form["delete_annot_doc_id"])
            print("delete_annot_doc_id:", delete_annot_doc_id)
            add_qc_doc_id = int(request.form["add_qc_doc_id"])  # which doc will be added to qc by current user
            print("add_qc_doc_id:", add_qc_doc_id)
            rm_qc_doc_id= int(request.form["rm_qc_doc_id"])
            print("rm_qc_doc_id", rm_qc_doc_id)
            rm_qc_user_id = int(request.form["rm_qc_user_id"])
            print("rm_qc_user_id", rm_qc_user_id)
            add_da_doc_id = int(request.form["add_da_doc_id"])
            print("add_da_doc_id: ", add_da_doc_id)
            rm_da_doc_id = int(request.form["rm_da_doc_id"])
            print("rm_da_doc_id: ", rm_da_doc_id)
            rm_da_user_id = int(request.form["rm_da_user_id"])
            print("rm_da_user_id: ", rm_da_user_id)
            if new_member_name:
                try: #add new member
                    new_member_user_id = User.query.filter(User.username==new_member_name).first().id
                    existing_member_of_this_project = Projectuser.query.filter(Projectuser.user_id==new_member_user_id, Projectuser.project_id==project_id).first()
                    if not existing_member_of_this_project:
                        project_name = Project.query.filter(Project.id==project_id).first().project_name
                        projectuser = Projectuser(project_name=project_name, user_id=new_member_user_id, permission="view", project_id=project_id)
                        db.session.add(projectuser)
                        db.session.commit()
                except Exception as e:
                    flash('username does not exist', 'danger')
                    print(e)
            elif remove_member_id !=0:
                Projectuser.query.filter(Projectuser.user_id==remove_member_id, Projectuser.project_id==project_id).delete()
                db.session.commit()
            elif update_doc_id !=0: #delete this doc: including all annotations, sents, docqcs, and docdas
                print("haha")
                Annotation.query.filter(Annotation.doc_id==update_doc_id).delete()
                Sent.query.filter(Sent.doc_id==update_doc_id).delete()
                Docqc.query.filter(Docqc.doc_id==update_doc_id).delete()
                Docda.query.filter(Docda.doc_id==update_doc_id).delete()
                Doc.query.filter(Doc.id == update_doc_id, Doc.user_id == current_user.id).delete()
                logging.info(db.session.commit())
                db.session.commit()
            elif annotated_doc_id !=0: #add to My Annotations
                print("I am here 33")
                # find dummy user
                dummy_user_id = User.query.filter(User.username=="dummy_user").first().id
                print(dummy_user_id)
                if not Annotation.query.filter(Annotation.doc_id==annotated_doc_id, Annotation.user_id==current_user.id).all():
                    for i in range(len(Sent.query.filter(Sent.doc_id==annotated_doc_id).all())):
                        # find the annotation rows belong to dummy
                        dummy_annotation = Annotation.query.filter(Annotation.doc_id==annotated_doc_id, Annotation.sent_id==i+1, Annotation.user_id==dummy_user_id).first()
                        if dummy_annotation:
                            print('I am here 35')
                            annotation = Annotation(sent_annot=dummy_annotation.sent_annot, doc_annot=dummy_annotation.doc_annot, alignment=dummy_annotation.alignment, user_id=current_user.id,
                                                    sent_id=dummy_annotation.sent_id, doc_id=dummy_annotation.doc_id, sent_umr=dummy_annotation.sent_umr, doc_umr=dummy_annotation.doc_umr)
                            db.session.add(annotation)
                        else:
                            print('I am here 36')
                            annotation = Annotation(sent_annot='',
                                                    doc_annot='',
                                                    alignment={}, user_id=current_user.id,
                                                    sent_id=i+1, doc_id=annotated_doc_id,
                                                    sent_umr={}, doc_umr={})
                            db.session.add(annotation)
                    logging.info(f"User {current_user.id} committed:")
                    logging.info(db.session.commit())
            elif delete_annot_doc_id !=0:
                print("I am here 34")
                Annotation.query.filter(Annotation.user_id==current_user.id, Annotation.doc_id==delete_annot_doc_id).delete()
                logging.info(db.session.commit())
                flash("file is removed from My Annotations", 'info')
            elif add_qc_doc_id !=0: # add to Quality Control
                qc_id = Project.query.filter(Project.id == project_id).first().qc_user_id # find the default qc user
                qc = User.query.filter(User.id==qc_id).first()  #get the project owner, who is the qc owner
                print("qc_id:", qc.id)
                # check existing:
                if not (Annotation.query.filter(Annotation.doc_id == add_qc_doc_id, Annotation.user_id == qc_id).all()):
                    print("I am here 70")
                    member_annotations = Annotation.query.filter(Annotation.doc_id == add_qc_doc_id, Annotation.user_id == current_user.id).all()
                    print('I am here 244')
                    for a in member_annotations:
                        qc_annotation = Annotation(sent_annot=a.sent_annot, doc_annot=a.doc_annot, alignment=a.alignment, user_id=qc_id,
                                                   sent_id=a.sent_id, doc_id=a.doc_id, sent_umr=a.sent_umr, doc_umr=a.doc_umr)
                        db.session.add(qc_annotation)
                    print('I am here 249')
                    docqc = Docqc(doc_id=add_qc_doc_id, project_id=project_id, upload_member_id=current_user.id) #document which member uploaded the qc doc of this project
                    db.session.add(docqc)
                    print('I am here 253')
                    logging.info(db.session.commit())
                    #
                    #     #Jiawei's'
                    #     docqc = Docqc(doc_id=add_qc_doc_id, project_id=project_id, upload_member_id=current_user,
                    #                   sent_annot=a.sent_annot, doc_annot=a.doc_annot, alignment=a.alignment, qc_user_id=qc,
                    #                   sent_id=a.sent_id, sent_umr=a.sent_umr, doc_umr=a.doc_umr)

                        # db.session.add(docqc)

                else:
                    flash('this file already exist in Quality Control, add to double annotated files instead', 'info')
            elif rm_qc_doc_id != 0 and rm_qc_user_id !=0: # delete from Quality Control
                current_qc_id = Project.query.filter(Project.id==project_id).first().qc_user_id
                Annotation.query.filter(Annotation.user_id==current_qc_id, Annotation.doc_id==rm_qc_doc_id).delete()
                Docqc.query.filter(Docqc.project_id==project_id, Docqc.doc_id==rm_qc_doc_id).delete()
                logging.info(db.session.commit())
                return redirect(url_for('users.project', project_id=project_id))
            elif add_da_doc_id !=0:
                #check existing:
                if not Docda.query.filter(Docda.project_id==project_id, Docda.user_id==current_user.id, Docda.doc_id==add_da_doc_id).all():
                    docda = Docda(project_id=project_id, user_id=current_user.id, doc_id=add_da_doc_id)
                    db.session.add(docda)
                    print('I am here for 275')
                    # docqc = Docqc.query.filter(Docqc.project_id==project_id, Docqc.doc_id==add_da_doc_id, Docqc.upload_member_id!=current_user.id).first()
                    # Jiawei.3

                    da_member_annotations = Annotation.query.filter(Annotation.doc_id == add_da_doc_id,
                                                                 Annotation.user_id == current_user.id).all()
                    print(len(da_member_annotations), 'how many da_annotations')
                    for a in da_member_annotations:
                        docda = Docda(project_id=project_id, user_id=current_user.id, doc_id=add_da_doc_id,
                                      sent_annot=a.sent_annot, doc_annot=a.doc_annot, alignment=a.alignment,
                                                   sent_id=a.sent_id, sent_umr=a.sent_umr, doc_umr=a.doc_umr)
                        db.session.add(docda)
                    print('reach 286')
                    # end
                    docqc = Docqc.query.filter(Docqc.project_id==project_id, Docqc.doc_id==add_da_doc_id,
                                               Docqc.upload_member_id!=current_user.id).first() # any other users upload the annotation as qc
                    print("docqc: ", docqc)
                    if docqc: #if there is a qc version of this doc already
                        print('I am here for 292')
                        if not Docda.query.filter(Docda.project_id == project_id, Docda.user_id == docqc.upload_member_id,
                                                  Docda.doc_id == add_da_doc_id).all(): #the user who uploaded the qc but not  created one da
                            # docda_qc = Docda(project_id=project_id, user_id=docqc.upload_member_id, doc_id=add_da_doc_id) # create a da for the user
                            # db.session.add(docda_qc)
                    #JIaiwe
                            qc_annotations = Annotation.query.filter(Annotation.doc_id == add_da_doc_id, Annotation.user_id==docqc.upload_member_id).all()
                            #
                            for a in qc_annotations:
                                docda_qc = Docda(project_id=project_id, user_id=docqc.upload_member_id,
                                                 doc_id=add_da_doc_id, sent_annot=a.sent_annot,
                                                 doc_annot=a.doc_annot, alignment=a.alignment, sent_id=a.sent_id,
                                                 sent_umr=a.sent_umr, doc_umr=a.doc_umr)
                                db.session.add(docda_qc)
                            # da_qc_member_annotations = Annotation.query.filter(Annotation.doc_id == add_da_doc_id,
                    logging.info(db.session.commit())
            elif rm_da_doc_id != 0 and rm_da_user_id != 0:
                print("I am here 66")
                Docda.query.filter(Docda.project_id==project_id, Docda.user_id==rm_da_user_id, Docda.doc_id==rm_da_doc_id).delete()
                logging.info(db.session.commit())
        except Exception as e:
            print(e)
            print("updating project in database is failed")

        try:
            edit_permission = request.get_json(force=True)["edit_permission"]
            print("edit_permission:", edit_permission)
            edit_permission_member_id = int(request.get_json(force=True)["edit_permission_member_id"])
            print("edit_permission_member_id", edit_permission_member_id)
            projectuser = Projectuser.query.filter(Projectuser.user_id == edit_permission_member_id,
                                                   Projectuser.project_id == project_id).first()
            projectuser.permission = edit_permission
            flag_modified(projectuser, 'permission')
            logging.info(f"project {projectuser.id} permission changed to {projectuser.permission}")
            logging.info(db.session.commit())
            db.session.commit()
        except Exception as e:
            print(e)
            print("If you are trying to change permission, permission change failed")
        return redirect(url_for('users.project', project_id=project_id))
    elif request.method == 'GET':
        form.projectname.data = project_name


    project_members = Projectuser.query.filter(Projectuser.project_id == project_id).all()
    members = []
    permissions = []
    member_ids = []
    for row in project_members:
        members.append(User.query.filter(User.id==row.user_id).first())
        permissions.append(row.permission)
        member_ids.append(row.user_id)

    current_permission = Projectuser.query.filter(Projectuser.user_id == current_user.id,
                                                  Projectuser.project_id == project_id).first().permission
    daDocs = Docda.query.filter(Docda.project_id == project_id).distinct(Docda.doc_id).all()
    # daDocs = Docda.query.filter(Docda.project_id == project_id, Docda.sent_id == 1).all() #sent_id = 1, so each file
    #     # only appear once

    daUploaders = []
    daFilenames = []
    for daDoc in daDocs:
        daUploaders.append(User.query.filter(User.id == daDoc.user_id).first().username)
        daFilenames.append(Doc.query.filter(Doc.id == daDoc.doc_id).first().filename)

    projectDocs = Doc.query.filter(Doc.project_id == project_id).all()
    checked_out_by = []
    qcAnnotations = Annotation.query.filter(Annotation.user_id == Project.query.get(int(project_id)).qc_user_id, Annotation.sent_id == 1).all() #when add to my annotation, annotation row of sent1 got added in Annotation table, therefore check if there is annotation for sent1
    qcDocs = []
    qcUploaders = []
    qcUploaderIds = []
    qcProjectIds= []
    for qca in qcAnnotations:
        qcDocs.append(Doc.query.filter(Doc.id==qca.doc_id).first()) # which docs were added
        uploader_id = Docqc.query.filter(Docqc.doc_id==qca.doc_id, Docqc.project_id==project_id).first().upload_member_id # who add the qc
        qcUploaderIds.append(uploader_id)  #get the uploader id
        qcUploaders.append(User.query.filter(User.id==uploader_id).first().username)  #the name of the uploader
        qcProjectIds.append(Project.query.get(int(project_id)).qc_user_id)  # this is for get the QC folder
    annotatedDocs = []
    for projectDoc in projectDocs:
        if Annotation.query.filter(Annotation.doc_id == projectDoc.id, Annotation.user_id==current_user.id).all():
            annotatedDocs.append(projectDoc)
        checked_out_docs = Annotation.query.filter(Annotation.doc_id == projectDoc.id).all()
        current_checked_out_by = set()
        if checked_out_docs:
            for d in checked_out_docs:
                user_name = User.query.filter(User.id==d.user_id).first().username
                if not user_name.endswith('_qc') and user_name != 'dummy_user':
                    current_checked_out_by.add(user_name)
        checked_out_by.append(list(current_checked_out_by))
    dummy_user_id = User.query.filter(User.username=='dummy_user').first().id

    return render_template('project.html', title='project', project_name=project_name, project_id=project_id,
                            members=members, permissions=permissions, member_ids=member_ids, checked_out_by=list(checked_out_by),
                           projectDocs=projectDocs, qcDocs=qcDocs, qcUploaders=qcUploaders, qcUploaderIds=qcUploaderIds, annotatedDocs=annotatedDocs,
                           daDocs=daDocs, daUploaders=daUploaders,  daFilenames=daFilenames, permission=current_permission,
                           form=form, dummy_user_id=dummy_user_id,qcProjectIds=qcProjectIds)

@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', default=1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=2)
    return render_template('user_post.html', posts=posts, user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:  # make sure they are logged out
        return redirect(url_for('main.display_post'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.display_post'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid token or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@users.route('/search/<string:project_id>', methods=['GET', 'POST'])
def search(project_id):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    # member_id = request.args.get('member_id', 1)
    print(request.args.items(), 'test426', request.get_json())
    # print(member_id, 'test395', project_id, request.args.keys())
    for k, v in request.args.items():
        print('test429', k, v)
    search_umr_form = SearchUmrForm()
    umr_results = []
    sent_results = []

    if search_umr_form.validate_on_submit():
        concept = search_umr_form.concept.data
        word = search_umr_form.word.data
        triple = search_umr_form.triple.data
        user_name = search_umr_form.user_name.data
        project_name = search_umr_form.project_name.data
        record_type=search_umr_form.document_type.data
        # print('I am here to test record type',record_type)
        h, r, c = "", "", ""

        if triple:
            h, r, c = triple.split()
        qc_user_id =Project.query.with_entities(Project.qc_user_id).all()  # unspecify the project, all kinds of qc users
        # qc_user_id=db.session.query(Docqc.)
        print(qc_user_id,'here is 456')
        if project_name:  # get the Doc related to the specific project


            project = Project.query.filter(Project.project_name == project_name).first()


            if project is not None:

                docs = Doc.query.filter(Doc.project_id == project.id).all()

                qc_user_id=project.qc_user_id  #if the project exists, just specify the qc for this project   // the qc for the specific project

                # print(qc_user_id,'here is 466')
            else:

                return render_template('search.html', title='search', search_umr_form=search_umr_form,
                                       umr_results=None,
                                       sent_results=sent_results)


                # docs = Doc.query.filter(Doc.project_id == project_id).all()  # find all the docs that belongs to the current project
        else:
            docs = Doc.query.all()

        doc_ids = [doc.id for doc in docs]  # record all the id of files in this project
        target_user = User.query.filter_by(username=user_name).first()  # the user specified
        # project_name = Project.query.filter(Project.id == project_id).first().project_name  # current project name.
        # print(isinstance(qc_user_id,int),type(qc_user_id),'here is 480',list(qc_user_id))
        '''
        get qc_ids into a list no matter the qc is for one project or all. 
        '''
        qc_user_ids = [qc_user_id] if isinstance(qc_user_id, int) else [r[0] for r in qc_user_id]


        for doc_id in doc_ids:
            sents = Sent.query.filter(Sent.doc_id == doc_id).all()  # all corresponding raw sentences
            sents.sort(key=lambda x: x.id)
            # if not search_project:  # this is all qc annotations, unspecicified projects

            annots_qc = Annotation.query.filter(and_(Annotation.doc_id == doc_id, Annotation.user_id != 3,  #exlude the dummny_user
                                                     Annotation.user_id.in_(qc_user_ids),
                                                     Annotation.sent_annot is not None,Annotation.sent_annot!='')).all()  # exclude the empty annotation
            print(annots_qc,'here is 491',qc_user_ids)


            if target_user:
                # qc_users=Docqc.query.filter(Docqc.upload_member_id==target_user.id,Docqc.doc_id==doc_id)
                annots = Annotation.query.filter(and_(Annotation.doc_id == doc_id,
                                                      Annotation.user_id == target_user.id,Annotation.sent_annot!='',Annotation.sent_annot is not None )).all()  # get the specific user if user specific the name
                qc_projects_for_user=Docqc.query.filter(Docqc.upload_member_id==target_user.id).first()
                if qc_projects_for_user:
                    qc_user_id_for_user=Project.query.filter(Project.id==qc_projects_for_user.project_id).first().qc_user_id  #get the qc annotations for the user
                    annots_qc= Annotation.query.filter(and_(Annotation.doc_id == doc_id,
                                                             Annotation.user_id == qc_user_id_for_user,
                                                             Annotation.sent_annot is not None,Annotation.sent_annot!='')).all()
                else:
                    annots_qc=[]
                annots=annots+annots_qc  #when specifying the user, just returning the normal annotations and his/her qc annotation
                if record_type=='qc':
                    annots=annots_qc
            else:
                print('here is 507')  # if not specify the user, just get all normal annotations
                annots = Annotation.query.filter(Annotation.doc_id == doc_id,   #here the query also include the qc annotations
                                                 Annotation.user_id != 3,
                                                 Annotation.sent_annot is not None).all()  # all the annotations for such docs
                print(annots,'here is 510',record_type)
                if record_type == 'qc': # if just qc
                    print(record_type)
                    annots = annots_qc  #then just return the qc annotations for the selected projects
                    #otherwise, return all annotation



            for annot in annots:
                sent = sents[annot.sent_id - 1]
                # the corresponding raw text for each annotation
                umr_dict = dict(annot.sent_umr)
                values = [v for k, v in umr_dict.items() if ('.s' in str(k)) or ('.c' in str(k))]
                if word:

                    if str(word).lower() in str(sent.content).strip().lower():
                        print(sents)
                        print('Iam1')
                        print(sent.content, '453-', annot.sent_annot, sents.index(sent), annot.id)
                        user_cur=User.query.filter(User.id == annot.user_id).first()
                        user_name = user_cur.username
                        record_type1='annotation'  # default type of record

                        current_doc = Doc.query.filter(Doc.id == doc_id).first()
                        file_name = current_doc.filename
                        project_cur = Project.query.filter(
                            Project.id == current_doc.project_id).first()  # current project
                        if user_cur.id in qc_user_ids:  # if the current user id is in the qc user ids,. that means current annotation is a qc version
                            record_type1 = 'qc_annotation'
                            qc_doc=Docqc.query.filter(Docqc.project_id ==project_cur.id,Docqc.doc_id==current_doc.id).first()   # get the corresponding record in the Docqc
                            '''we will not use the annotation.user_id to get the user name,because it will return xxxx_qc rather than true username, thus we need to get the qc record and find the upload member'''
                            user_name=User.query.filter(User.id==qc_doc.upload_member_id).first().username
                        project_name=project_cur.project_name
                        umr_results.append(
                            (sent.content,
                             annot.sent_annot.replace(' ', '&nbsp;').replace('\n', '<br>'), user_name,file_name,project_name,record_type1))
                        # continue
                        sent_results.append(sent.content)

                elif concept:
                    # umr_dict = dict(annot.sent_umr)
                    # values = [v for k, v in umr_dict.items() if ('.s' in str(k)) or ('.c' in str(k))]
                    # print(str(concept), getLemma(str(concept),upos="VERB"),'483')

                    for value in values:
                        if re.search('-\d+', str(concept)):
                            condition = (str(concept) in str(value))
                        else:
                            condition = (str(concept) in str(value)) or (
                                    getLemma(str(concept), upos="VERB")[0] in str(value))
                        if condition:
                            # or (getLemma(str(concept), upos="VERB")[0] in str(value)):
                            print('Iam2', sent.content)
                            print('test453', concept, value, getLemma(word, upos="VERB")[0])
                            # todo: bug: sent didn't got returned
                            # sent = Sent.query.filter(Sent.doc_id == doc_id).all()[annot.sent_id - 1]
                            user_cur = User.query.filter(User.id == annot.user_id).first()
                            user_name=user_cur.username
                            current_doc = Doc.query.filter(Doc.id == doc_id).first()
                            file_name = current_doc.filename
                            project_name = Project.query.filter(
                                Project.id == current_doc.project_id).first().project_name
                            record_type1='annotation'
                            if user_cur.id in qc_user_ids:
                                record_type1 = 'qc_annotation'
                                docqc=Docqc.query.filter(Docqc.project_id == current_doc.project_id,
                                                   Docqc.doc_id == current_doc.id).first()
                                user_name = User.query.filter(User.id == docqc.upload_member_id).first().username
                            umr_results.append(
                                # '<hr flex-grow: 1 class="separate_line">'+sent.content + '<hr/>'+'<hr  flex-grow: 1 class="separate_line">'+annot.sent_annot.replace(' ', '&nbsp;').replace('\n', '<br>') + "</hr>"+'<hr>' + user_name.username + '<hr/>' + '<hr>'  + '</hr')
                                (sent.content, annot.sent_annot.replace(' ', '&nbsp;').replace('\n', '<br>'),
                                 user_name, file_name, project_name,record_type1))
                            sent_results.append(sent.content)
                            print(umr_results, sent_results, 'test422')

                else:
                    if triple:
                        # umr_dict = dict(annot.sent_umr)
                        # values = [v for k, v in umr_dict.items() if ('.s' in str(k)) or ('.c' in str(k))]
                        for value in values:
                            if c and (c in str(value) or getLemma(c, upos="VERB")[0] in str(value)):

                                print('Iam3')
                                k = list(umr_dict.keys())[list(umr_dict.values()).index(value)]
                                print(k,"I am test k 580",umr_dict)
                                if umr_dict.get(k.replace(".c", '.r'), "") == r and (
                                    h == "*" or h == umr_dict.get('.'.join(k.strip().split('.')[:-2])+'.c', "")):
                                    print('I am here to test triples query')
                                    user_name = User.query.filter(User.id == annot.user_id).first().username
                                    current_doc = Doc.query.filter(Doc.id == doc_id).first()
                                    file_name = current_doc.filename
                                    cur_project=Project.query.filter(
                                        Project.id == current_doc.project_id).first()
                                    project_name = cur_project.project_name
                                    record_type1='annotation'
                                    if user_name.id in qc_user_ids:
                                        record_type1 = 'qc_annotation'
                                        docqc=Docqc.query.filter(Docqc.project_id == current_doc.project_id,
                                                           Docqc.doc_id == current_doc.id).first()
                                        user_name = User.query.filter(
                                            User.id == docqc.upload_member_id).first().username
                                    umr_results.append(
                                        # '<hr flex-grow: 1 class="separate_line">'+sent.content + '<hr/>'+'<hr  flex-grow: 1 class="separate_line">'+annot.sent_annot.replace(' ', '&nbsp;').replace('\n', '<br>') + "</hr>"+'<hr>' + user_name.username + '<hr/>' + '<hr>'  + '</hr')
                                        (sent.content, annot.sent_annot.replace(' ', '&nbsp;').replace('\n', '<br>'),
                                         user_name, file_name, project_name,record_type1))
                                    sent_results.append(sent.content)

    return render_template('search.html', title='search', search_umr_form=search_umr_form, umr_results=umr_results,
                           sent_results=sent_results) 



@users.route('/partialgraph/<int:project_id>', methods=['GET', 'POST'])
def partialgraph(project_id):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    project_name = Project.query.filter(Project.id == project_id).first().project_name
    partialGraphs = Partialgraph.query.filter(Partialgraph.project_id == project_id).first().partial_umr
    print("partialGraphs: ", type(partialGraphs))
    if request.method == "POST":
        try:
            partialGraphKey = request.get_json(force=True)['partialGraphKey']
            del partialGraphs[partialGraphKey]
            partial_graph_to_change = Partialgraph.query.filter(Partialgraph.project_id == project_id).first()
            partial_graph_to_change.partial_umr = partialGraphs
            flag_modified(partial_graph_to_change, "partial_umr")
            db.session.commit()
        except Exception as e:
            print(e)
            print("delete partial graph error")
    return render_template('partial_graph.html', title='partial graphs', partialGraphs=partialGraphs, project_name=project_name, project_id=project_id)

@users.route('/alllexicon/<int:project_id>', methods=['GET', 'POST'])
def alllexicon(project_id):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    project_name = Project.query.filter(Project.id == project_id).first().project_name
    lexi = Lexicon.query.filter(Lexicon.project_id == project_id).first().lexi
    lexi = dict(lexi)
    if request.method == "POST":
        print("request.get_json(force=True): ", request.get_json(force=True))
        deleteLemmaKey = request.get_json(force=True)['deleteLemmaKey']
        changeLemmaKey = request.get_json(force=True)['changeLemmaKey']
        entry = request.get_json(force=True)['entry']
        share2projectName = request.get_json(force=True)['share2projectName']
        deleteLexicon = request.get_json(force=True)['deleteLexicon']
        if deleteLemmaKey:
            try:
                del lexi[deleteLemmaKey]
                lexi_to_change = Lexicon.query.filter(Lexicon.project_id == project_id).first()
                lexi_to_change.lexi = lexi
                flag_modified(lexi_to_change, "lexi")
                db.session.commit()
                return make_response(jsonify({"msg": "delete entry: success", "msg_category": "success"}), 200)
            except Exception as e:
                print(e)
                print("delete lexicon error")
        elif changeLemmaKey:
            try:
                lexi_to_change = Lexicon.query.filter(Lexicon.project_id == project_id).first()
                original_lexi = dict(lexi_to_change.lexi)
                original_lexi[changeLemmaKey] = json.loads(entry)
                lexi_to_change.lexi = original_lexi
                flag_modified(lexi_to_change, "lexi")
                db.session.commit()
                return make_response(jsonify({"msg": "change entry: success", "msg_category": "success"}), 200)
            except Exception as e:
                print(e)
                print("edit lexicon error")

        elif share2projectName:
            try:
                share2projectId = Projectuser.query.filter(Projectuser.project_name == share2projectName, Projectuser.user_id == current_user.id).first().project_id
                lexi2change = Lexicon.query.filter(Lexicon.project_id == share2projectId).first()
                lexi2change.lexi = Lexicon.query.filter(Lexicon.project_id == project_id).first().lexi
                flag_modified(lexi2change, "lexi")
                db.session.commit()
                return make_response(jsonify({"msg": "share lexicon: success", "msg_category": "success"}), 200)
            except Exception as e:
                print(e)
                print("share lexicon with your other project error")
        elif deleteLexicon:
            try:
                lexi_to_change = Lexicon.query.filter(Lexicon.project_id == project_id).first()
                lexi_to_change.lexi = {}
                flag_modified(lexi_to_change, "lexi")
                db.session.commit()
                return make_response(jsonify({"msg": "delete whole lexicon successfully, refresh to see changes", "msg_category": "success"}), 200) #need refresh to see is because, redirect to current page, under post somehow doesn't work, therefore I will have to ask the user to refresh manually
            except Exception as e:
                print(e)
                print("delete lexicon error")

    all_projects = Projectuser.query.filter(Projectuser.user_id == current_user.id, Projectuser.permission=="admin").all()
    all_project_names = [p.project_name for p in all_projects]
    return render_template('alllexicon.html', title='all lexicon', lexi=json.dumps(lexi), project_name=project_name, project_id=project_id, all_projects=json.dumps(all_project_names))

# annotation lattices
@users.route('/discourse/<int:project_id>', methods=['GET', 'POST'])
def discourse(project_id):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    if request.method == 'POST':
        try:
            discourse_setting = request.get_json(force=True)['lattice_setting']
            lattice_setting = Lattice.query.filter(Lattice.project_id == project_id).first()
            lattice_setting.discourse = discourse_setting
            print("discourse_setting: ", discourse_setting)
            flag_modified(lattice_setting, 'discourse')
            db.session.commit()
            msg = 'Discourse settings are applied successfully.'
            msg_category = 'success'
            return make_response(jsonify({"msg": msg, "msg_category": msg_category}), 200)
        except Exception as e:
            print(e)
            print("get modal setting error")
    return render_template('discourse.html', project_id=project_id, current_setting=json.dumps(Lattice.query.filter(Lattice.project_id == project_id).first().discourse))

@users.route('/aspect/<int:project_id>', methods=['GET', 'POST'])
def aspect(project_id):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    if request.method == 'POST':
        try:
            aspect_setting = request.get_json(force=True)['lattice_setting']
            lattice_setting = Lattice.query.filter(Lattice.project_id == project_id).first()
            lattice_setting.aspect = aspect_setting
            print("aspect_setting: ", aspect_setting)
            flag_modified(lattice_setting, 'aspect')
            db.session.commit()
            msg = 'Aspect settings are applied successfully.'
            msg_category = 'success'
            return make_response(jsonify({"msg": msg, "msg_category": msg_category}), 200)
        except Exception as e:
            print(e)
            print("get aspect setting error")
    return render_template('aspect.html', project_id=project_id, current_setting=json.dumps(Lattice.query.filter(Lattice.project_id == project_id).first().aspect))

@users.route('/person/<int:project_id>', methods=['GET', 'POST'])
def person(project_id):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    if request.method == 'POST':
        try:
            person_setting = request.get_json(force=True)['lattice_setting']
            lattice_setting = Lattice.query.filter(Lattice.project_id == project_id).first()
            lattice_setting.person = person_setting
            print("person_setting: ", person_setting)
            flag_modified(lattice_setting, 'person')
            db.session.commit()
            msg = 'Person settings are applied successfully.'
            msg_category = 'success'
            return make_response(jsonify({"msg": msg, "msg_category": msg_category}), 200)
        except Exception as e:
            print(e)
            print("get person setting error")
    return render_template('person.html', project_id=project_id, current_setting=json.dumps(Lattice.query.filter(Lattice.project_id == project_id).first().person))

@users.route('/number/<int:project_id>', methods=['GET', 'POST'])
def number(project_id):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    if request.method == 'POST':
        try:
            number_setting = request.get_json(force=True)['lattice_setting']
            lattice_setting = Lattice.query.filter(Lattice.project_id == project_id).first()
            lattice_setting.number = number_setting
            print("number_setting: ", number_setting)
            flag_modified(lattice_setting, 'number')
            db.session.commit()
            msg = 'Number settings are applied successfully.'
            msg_category = 'success'
            return make_response(jsonify({"msg": msg, "msg_category": msg_category}), 200)
        except Exception as e:
            print(e)
            print("get number setting error")
    return render_template('number.html', project_id=project_id, current_setting=json.dumps(Lattice.query.filter(Lattice.project_id == project_id).first().number))

@users.route('/modal/<int:project_id>', methods=['GET', 'POST'])
def modal(project_id):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    if request.method == 'POST':
        try:
            modal_setting = request.get_json(force=True)['lattice_setting']
            lattice_setting = Lattice.query.filter(Lattice.project_id == project_id).first()
            lattice_setting.modal = modal_setting
            flag_modified(lattice_setting, 'modal')
            db.session.commit()
            msg = 'Modal settings are applied successfully.'
            msg_category = 'success'
            return make_response(jsonify({"msg": msg, "msg_category": msg_category}), 200)
        except Exception as e:
            print(e)
            print("get modal setting error")
    return render_template('modal.html', project_id=project_id, current_setting=json.dumps(Lattice.query.filter(Lattice.project_id == project_id).first().modal))

@users.route('/modification/<int:project_id>', methods=['GET', 'POST'])
def modification(project_id): #there is no post here like the previous ones, because users are not allowed to toggle off any modification items in the dropdown menu
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    return render_template('modification.html', project_id=project_id)



@users.route('/settings/<int:project_id>', methods=['GET', 'POST'])
def settings(project_id):
        return render_template('settings.html', project_id=project_id)

@users.route('/exproted_all_files/<int:project_id>',methods=['GET','POST'])
def exported_all_files(project_id):
    print(project_id,'392')
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    Doc_id_list=Doc.query.filter(Doc.project_id==project_id).all()
    exported_items_dict=[]
    content_string_dict=[]
    doc_name_dict=[]
    project_name=Project.query.filter(Project.id==project_id).first().project_name
    # exported_items=''
    # content_string=''
    # doc_name=''
    meta_data=[]
    for doc in Doc_id_list:
        doc_id=doc.id
        language=doc.lang
        file_format=doc.file_format
        # doc=Doc.query.get_or_404(int(doc_id.id))
        doc_name=doc.filename
        user_id=current_user.id
        user_name=User.query.filter(User.id==user_id).first().username
        meta_data.append([user_name, user_id, language, file_format, doc_id])
        annotations = Annotation.query.filter(Annotation.doc_id == doc_id,
                                              Annotation.user_id == user_id).order_by(
            Annotation.sent_id).all()
        filtered_sentences = Sent.query.filter(Sent.doc_id == doc_id).order_by(Sent.id).all()
        all_sents = [sent2.content for sent2 in filtered_sentences]
        all_annots = [annot.sent_annot for annot in annotations]
        all_aligns = [annot.alignment for annot in annotations]
        all_doc_annots = [annot.doc_annot for annot in annotations]
        sent_with_annot_ids = [annot.sent_id for annot in annotations]
        all_annots_no_skipping = [""] * len(all_sents)
        all_aligns_no_skipping = [""] * len(all_sents)
        all_doc_annots_no_skipping = [""] * len(all_sents)
        for i, sa, a, da in zip(sent_with_annot_ids, all_annots, all_aligns, all_doc_annots):
            all_annots_no_skipping[i - 1] = sa
            all_aligns_no_skipping[i - 1] = a
            all_doc_annots_no_skipping[i - 1] = da
        exported_items = [list(p) for p in
                          zip(all_sents, all_annots_no_skipping, all_aligns_no_skipping, all_doc_annots_no_skipping)]

        exported_items_dict.append(exported_items)
        content_string_dict.append(doc.content.replace('\\', '\\\\'))
        doc_name_dict.append(doc_name)

        # print(exported_items,doc.content,'424')
        # content_string = doc.content.replace('\\', '\\\\')
    return render_template('exported_all_files.html',
                           exported_items_dict=exported_items_dict,content_string_dict=content_string_dict,
                           doc_name_dict=doc_name_dict,project_name=project_name,meta_data=meta_data)
