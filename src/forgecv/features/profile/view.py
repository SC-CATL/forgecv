"""个人信息页：基本资料与证书维护。"""

from __future__ import annotations

from typing import Any, cast

from forgecv.features.profile.schemas import CandidateInput, CertificateInput
from forgecv.features.profile.viewmodel import ProfileViewModel
from forgecv.platform.ui.kit import forms
from forgecv.platform.ui.qt import QtCore, QtWidgets

FIELDS = (
    ("full_name", "姓名"),
    ("headline", "求职意向"),
    ("city", "城市"),
    ("email", "邮箱"),
    ("phone", "电话"),
    ("github_url", "GitHub"),
    ("blog_url", "博客"),
    ("website_url", "个人主页"),
)


class ProfilePage(QtWidgets.QWidget):
    """左侧无需导航，整页就是一表单加一列表。"""

    def __init__(self, view_model: ProfileViewModel) -> None:
        """构建页面并加载数据。"""
        super().__init__()
        self._vm = view_model
        self._edits: dict[str, QtWidgets.QLineEdit] = {}
        self._summary: QtWidgets.QTextEdit
        self._certificates: QtWidgets.QListWidget
        self._cert_name: QtWidgets.QLineEdit
        self._cert_issuer: QtWidgets.QLineEdit
        self._cert_date: QtWidgets.QDateEdit
        self._status: QtWidgets.QLabel

        area, layout = forms.scroll_form(self)
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(area)

        layout.addWidget(forms.title("个人信息", area))
        layout.addWidget(forms.muted("数据只存在本机，用于生成简历与能力分析。", area))
        layout.addWidget(self._build_basic(area))
        layout.addWidget(self._build_certificates(area))
        self._status = forms.muted("", area)
        layout.addWidget(self._status)
        layout.addStretch(1)

        self._vm.status_changed.connect(self._status.setText)
        self._vm.candidate_changed.connect(self._fill)
        self._vm.certificates_changed.connect(self._fill_certificates)
        self._vm.load()

    def _build_basic(self, parent: QtWidgets.QWidget) -> QtWidgets.QFrame:
        """基本信息卡片。"""
        frame, layout = forms.card(parent)
        layout.addWidget(forms.title("基本信息", frame))
        body = forms.form()
        for key, label in FIELDS:
            edit = QtWidgets.QLineEdit(frame)
            self._edits[key] = edit
            body.addRow(label, edit)
        self._summary = QtWidgets.QTextEdit(frame)
        self._summary.setFixedHeight(90)
        body.addRow("自我评价", self._summary)
        layout.addLayout(body)
        row = QtWidgets.QHBoxLayout()
        row.addStretch(1)
        save = forms.button("保存", frame)
        save.clicked.connect(self._save)
        row.addWidget(save)
        layout.addLayout(row)
        return frame

    def _build_certificates(self, parent: QtWidgets.QWidget) -> QtWidgets.QFrame:
        """证书卡片：列表 + 快速新增。"""
        frame, layout = forms.card(parent)
        layout.addWidget(forms.title("证书与荣誉", frame))
        self._certificates = QtWidgets.QListWidget(frame)
        self._certificates.setObjectName("ItemList")
        self._certificates.setFixedHeight(120)
        self._certificates.currentRowChanged.connect(self._sync_cert_buttons)
        layout.addWidget(self._certificates)

        row = QtWidgets.QHBoxLayout()
        self._cert_name = QtWidgets.QLineEdit(frame)
        self._cert_name.setPlaceholderText("证书名称")
        self._cert_issuer = QtWidgets.QLineEdit(frame)
        self._cert_issuer.setPlaceholderText("颁发机构")
        self._cert_date = forms.date_edit(frame)
        add = forms.button("添加", frame, secondary=True)
        add.clicked.connect(self._add_certificate)
        row.addWidget(self._cert_name, 2)
        row.addWidget(self._cert_issuer, 2)
        row.addWidget(self._cert_date)
        row.addWidget(add)
        layout.addLayout(row)

        actions = QtWidgets.QHBoxLayout()
        actions.addStretch(1)
        self._delete_cert = forms.button("删除选中", frame, danger=True)
        self._delete_cert.setEnabled(False)
        self._delete_cert.clicked.connect(self._delete_certificate)
        actions.addWidget(self._delete_cert)
        layout.addLayout(actions)
        return frame

    def _save(self) -> None:
        """收集表单并保存。"""
        data = CandidateInput(
            full_name=self._edits["full_name"].text(),
            headline=self._edits["headline"].text(),
            city=self._edits["city"].text(),
            email=self._edits["email"].text(),
            phone=self._edits["phone"].text(),
            github_url=self._edits["github_url"].text(),
            blog_url=self._edits["blog_url"].text(),
            website_url=self._edits["website_url"].text(),
            summary=self._summary.toPlainText(),
        )
        self._vm.save(data)

    def _fill(self, candidate: object) -> None:
        """把候选人数据写回表单。"""
        name = getattr(candidate, "full_name", "")
        for key, _label in FIELDS:
            value = getattr(candidate, key, "") if candidate is not None else ""
            self._edits[key].setText(str(value))
        self._summary.setPlainText(str(getattr(candidate, "summary", "")) if candidate else "")
        self._status.setText("已加载个人信息" if name else "尚未建档，填写后点击保存")

    def _fill_certificates(self, rows: object) -> None:
        """刷新证书列表。"""
        records = cast(list[Any], rows)
        self._certificates.clear()
        for row in records:
            issued = getattr(row, "issued_on", None)
            suffix = f" · {issued.isoformat()}" if issued else ""
            item = QtWidgets.QListWidgetItem(f"{row.name} · {row.issuer}{suffix}")
            item.setData(QtCore.Qt.ItemDataRole.UserRole, row.id)
            self._certificates.addItem(item)
        self._sync_cert_buttons()

    def _add_certificate(self) -> None:
        """用快速表单新增证书。"""
        data = CertificateInput(
            name=self._cert_name.text(),
            issuer=self._cert_issuer.text(),
            issued_on=forms.to_date(self._cert_date),
        )
        if self._vm.add_certificate(data):
            self._cert_name.clear()
            self._cert_issuer.clear()

    def _delete_certificate(self) -> None:
        """删除选中证书。"""
        item = self._certificates.currentItem()
        if item is not None:
            self._vm.delete_certificate(int(item.data(QtCore.Qt.ItemDataRole.UserRole)))

    def _sync_cert_buttons(self) -> None:
        """只有选中时才能删除。"""
        self._delete_cert.setEnabled(self._certificates.currentRow() >= 0)
