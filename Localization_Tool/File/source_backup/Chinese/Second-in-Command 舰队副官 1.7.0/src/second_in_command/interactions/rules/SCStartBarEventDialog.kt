package second_in_command.interactions.rules

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.campaign.*
import com.fs.starfarer.api.campaign.rules.MemKeys
import com.fs.starfarer.api.campaign.rules.MemoryAPI
import com.fs.starfarer.api.combat.EngagementResultAPI
import com.fs.starfarer.api.impl.campaign.ids.Sounds
import com.fs.starfarer.api.impl.campaign.rulecmd.BaseCommandPlugin
import com.fs.starfarer.api.impl.campaign.rulecmd.FireAll
import com.fs.starfarer.api.ui.Alignment
import com.fs.starfarer.api.ui.CustomPanelAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import lunalib.lunaExtensions.addLunaElement
import second_in_command.SCUtils
import second_in_command.misc.addPara
import second_in_command.misc.addTooltip
import second_in_command.specs.SCAptitudeSection
import second_in_command.specs.SCOfficer
import second_in_command.specs.SCSpecStore
import second_in_command.ui.elements.*
import second_in_command.ui.tooltips.OfficerTooltipCreator
import second_in_command.ui.tooltips.SCSkillTooltipCreator
import java.awt.Color

class SCStartBarEventDialog : BaseCommandPlugin() {
    override fun execute(ruleId: String?, dialog: InteractionDialogAPI, params: MutableList<Misc.Token>?, memoryMap: MutableMap<String, MemoryAPI>?): Boolean {
        dialog.optionPanel.clearOptions()

        var plugin = SCStartBarEventDialogDelegate(dialog.plugin)
        dialog.plugin = plugin
        plugin.init(dialog)

        return true
    }
}

class SCStartBarEventDialogDelegate(var original: InteractionDialogPlugin) : InteractionDialogPlugin {

    lateinit var dialog: InteractionDialogAPI
    lateinit var textPanel: TextPanelAPI
    lateinit var optionPanel: OptionPanelAPI

    var officers = ArrayList<SCOfficer>()

    override fun init(dialog: InteractionDialogAPI) {

        this.dialog = dialog
        this.textPanel = dialog.textPanel
        this.optionPanel = dialog.optionPanel

        var aptitudes = SCSpecStore.getAptitudeSpecs().map { it.getPlugin() }.filter { it.getTags().contains("startingOption") }
        for (aptitude in aptitudes) {
            var officer = SCUtils.createRandomSCOfficer(aptitude.getId(), dialog.interactionTarget.market.faction)
            officers.add(officer)
        }

        textPanel.addPara("你靠近那位看似在尝试推销各式合约的人，尽管到目前为止还一笔都没有成交过。")

        textPanel.addPara("\"哦哦，就是您！您一看就是那种野心勃勃、有朝一日会在星域里称霸一方；又或者出于自己的喜好，反而选择温情脉脉统御一方的那种星舰舰长！")

        textPanel.addPara("不过，这些宏伟目标永远不会在缺乏助力的情况下实现……所以您也许会对我们公司的服务感兴趣？\" 他看上去热情万分，但或者恰恰正是这份热情反而让他的陈述更显绝望。")

        optionPanel.addOption("听听他究竟能有什么提议", "HEAR_HIM_OUT")

        //optionPanel.addOption("Return", "RETURN")
    }

    fun returnToBar() {

        Global.getSector().memoryWithoutUpdate.set("\$sc_selectedStart", true)

        dialog.optionPanel.clearOptions()

        dialog.plugin = original
        dialog.visualPanel.hideFirstPerson()
        dialog.interactionTarget.activePerson = null
        (dialog.plugin as RuleBasedDialog).notifyActivePersonChanged()

        dialog.plugin.memoryMap.get(MemKeys.LOCAL)!!.set("\$option", "backToBar")
        FireAll.fire(null, dialog, memoryMap, "DialogOptionSelected")
    }

    fun chooseOfficer(officer: SCOfficer) {
        optionPanel.clearOptions()

        var data = SCUtils.getPlayerData()

        textPanel.addPara("> 选择一名 执行军官", Misc.getBasePlayerColor(), Misc.getBasePlayerColor())

        textPanel.addParagraph("${officer.person.nameString} (等级 ${officer.getCurrentLevel()}) 加入了你的舰队",  Misc.getPositiveHighlightColor())


        textPanel.addPara("\"上佳之选！我们诚挚希望您选择的执行军官能助力您离目标更进一步！希望您以后能继续与我们合作！")

        textPanel.addPara("\"您通常可以在各个殖民地的{通讯录}上找到我们公司的可用合同，当您需要更多执行军官时，请务必不吝赐教。\" 他挥挥手向你告别，继续寻找其他客户去了。",
        Misc.getTextColor(), Misc.getHighlightColor(), "通讯录")

        textPanel.addPara("你可以在你 Tri-Pad 的 \"角色\" 界面上查看新执行军官的更多信息。", Misc.getGrayColor(), Misc.getHighlightColor(), "角色")

        data.addOfficerToFleet(officer)
        data.setOfficerInEmptySlotIfAvailable(officer)


        optionPanel.addOption("返回酒吧", "LEAVE")
    }

    override fun optionSelected(optionText: String?, optionData: Any?) {

        if (optionData == "HEAR_HIM_OUT") {
            optionPanel.clearOptions()

            textPanel.addPara("> 听听他的提议", Misc.getBasePlayerColor(), Misc.getBasePlayerColor())

            textPanel.addPara("\"这才对嘛！我们公司专精于提供你们称之为{执行军官}的专业人士。 " +
                    "这类军官专精于运用各种独特{技能}为整支舰队提供各种支持，每名军官都有自己特别擅长的专属{天赋}。",
                Misc.getTextColor(), Misc.getHighlightColor(), "执行军官", "技能", "天赋")

            textPanel.addPara("作为特别促销活动的一部分，通过我们公司签署的第一份合同的所有开支将由我们全额支付，请把这视为对双方未来业务蒸蒸日上的良好祝愿！\" 你继续等他把话说完，隐约意识到究竟是什么让他们的业务陷入困境。 " +
                    "他继续开口，\"这儿，当前所有可用合约的一览表，请任选其中一位！\"")

            var tooltip = textPanel.beginTooltip()

            tooltip.addPara("军官名单分为 \"推荐\" 军官和 \"高级\" 军官。这两类执行军官对你的舰队都可能有用，但推荐之选能适用于大多数舰队。 ",
                0f, Misc.getGrayColor(), Misc.getHighlightColor(), "\"推荐\"", "\"Advanced\"")

            textPanel.addTooltip()

            optionPanel.addOption("选择一名 执行军官 (推荐)", "ACCEPT")
            optionPanel.addOption("拒绝他的提议", "DECLINE")

        }

        if (optionData == "ACCEPT") {
            var width = 1080f
            dialog.showCustomVisualDialog(width, 700f, SCBarDelegatePanel(this, officers, width))
        }

        if (optionData == "DECLINE") {

            optionPanel.clearOptions()

            textPanel.addPara("> 拒绝他的提议", Misc.getBasePlayerColor(), Misc.getBasePlayerColor())

            textPanel.addPara("\"多么遗憾……不过如果您以后有兴趣的话，还请再度与我们联系。\" 你听得出来，他每吐出一个字都变得更加颓唐。" +
                    "")

            textPanel.addPara("\"您通常可以在各个殖民地的 通讯录 上找到可用的合同。\" 他挥挥手向你告别，继续去寻找下一位客户了。", Misc.getTextColor(), Misc.getHighlightColor(), "通讯录")

            optionPanel.addOption("返回酒吧", "LEAVE")
        }

        if (optionData == "LEAVE") {
            textPanel.addPara("> 返回酒吧", Misc.getBasePlayerColor(), Misc.getBasePlayerColor())

            returnToBar()
        }

    }

    override fun optionMousedOver(optionText: String?, optionData: Any?) {

    }

    override fun advance(amount: Float) {

    }

    override fun backFromEngagement(battleResult: EngagementResultAPI?) {

    }

    override fun getContext(): Any? {
        return null
    }

    override fun getMemoryMap(): MutableMap<String, MemoryAPI> {
        return original.memoryMap
    }
}

class SCBarDelegatePanel(var plugin: SCStartBarEventDialogDelegate, var officers: List<SCOfficer>, var width: Float) : CustomVisualDialogDelegate {

    var selectedOfficer: SCOfficer? = null


    override fun init(panel: CustomPanelAPI?, callbacks: CustomVisualDialogDelegate.DialogCallbacks?) {


        var height = panel!!.position.height - 25

        var heightCap = 40f

        var scrollerPanel = panel.createCustomPanel(width, height - heightCap, null)
        panel.addComponent(scrollerPanel)
        scrollerPanel.position.inTL(0f, 0f)
        var scrollerElement = scrollerPanel.createUIElement(width, height - heightCap, true)

        var data = SCUtils.getPlayerData()

        var recommended = mutableListOf(
            "sc_tactical",
            "sc_management",
            "sc_engineering",
            "sc_starfaring",
        )

        //Recommended Header
        scrollerElement.addSpacer(10f)
        var recommendedHeader = scrollerElement.addSectionHeading("卖家推荐", Alignment.MID, 0f)
        recommendedHeader.position.setXAlignOffset(10f)
        recommendedHeader.position.setSize(recommendedHeader.position.width - 25, recommendedHeader.position.height)

        var officers = officers.sortedWith(compareBy({ !recommended.contains(it.aptitudeId ) }, { !it.isAssigned() }, { it.getAptitudeSpec().order }))
        for (officer in officers) {

            var aptitudeSpec = SCSpecStore.getAptitudeSpec(officer.aptitudeId)
            var aptitudePlugin = aptitudeSpec!!.getPlugin()

            var categories = aptitudePlugin.categories


            var extra = 0f
            if (categories.isNotEmpty()) extra += 20f
            scrollerElement.addSpacer(10f)
            var officerElement = scrollerElement.addLunaElement(width - 10, 96f + 36 + extra).apply {
                enableTransparency = true
                backgroundAlpha = 0.025f
                borderAlpha = 0.1f
                backgroundColor = aptitudePlugin.getColor()
                borderColor = aptitudePlugin.getColor()
            }


            officerElement.advance {
                if (officer == selectedOfficer) {
                    officerElement.backgroundAlpha = 0.15f
                    officerElement.borderAlpha = 0.35f
                }
                else if (officerElement.isHovering) {
                    officerElement.backgroundAlpha = 0.1f
                    officerElement.borderAlpha = 0.25f
                }
                else {
                    officerElement.backgroundAlpha = 0.025f
                    officerElement.borderAlpha = 0.1f
                }
            }



            officerElement.onClick {
                Global.getSoundPlayer().playUISound("ui_button_pressed", 1f, 1f)
                selectedOfficer = officer
            }


            var inner = officerElement.innerElement
            inner.addSpacer(24f)

            var officerPickerElement = SCOfficerPickerElement(officer.person, aptitudePlugin.getColor(), inner, 96f, 96f)
            officerPickerElement.onClick {
                Global.getSoundPlayer().playUISound("ui_button_pressed", 1f, 1f)
                selectedOfficer = officer
            }

            var paraElement = inner.addLunaElement(100f, 20f).apply {
                renderBorder = false
                renderBackground = false
            }
            paraElement.elementPanel.position.aboveMid(officerPickerElement.elementPanel, 0f)

            paraElement.innerElement.setParaFont("graphics/fonts/victor14.fnt")
            var aptitudePara = paraElement.innerElement.addPara(aptitudePlugin.getName(), 0f, aptitudePlugin.getColor(), aptitudePlugin.getColor())
            aptitudePara.position.inTL(paraElement.width / 2 - aptitudePara.computeTextWidth(aptitudePara.text) / 2 - 1, paraElement.height  -aptitudePara.computeTextHeight(aptitudePara.text)-5)


/*

            officerPickerElement.innerElement.setParaFont("graphics/fonts/victor14.fnt")
            var aptitudePara = officerPickerElement.innerElement.addPara(aptitudePlugin.getName(), 0f, aptitudePlugin.getColor(), aptitudePlugin.getColor())
            aptitudePara.position.inTL(officerPickerElement.width / 2 - aptitudePara.computeTextWidth(aptitudePara.text) / 2 - 1, -aptitudePara.computeTextHeight(aptitudePara.text)-5)
*/

            var offset = 10f
            var offsetElement = inner.addLunaElement(0f, 0f)
            offsetElement.elementPanel.position.rightOfMid(officerPickerElement.elementPanel, -1f)

            var background = AptitudeBackgroundElement(aptitudePlugin.getColor(), inner, true)
            //background.elementPanel.position.rightOfMid(officerPickerElement.elementPanel, -1f)
            background.elementPanel.position.belowLeft(offsetElement.elementPanel, offset)

            var officerUnderline = SkillUnderlineElement(aptitudePlugin.getColor(), 2f, inner, 96f)
            officerUnderline.position.belowLeft(officerPickerElement.elementPanel, 2f)

            /*aptitudePlugin.clearSections()
            aptitudePlugin.createSections()*/
            var sections = aptitudePlugin.getSections()

            var originSkill = SCSpecStore.getSkillSpec(aptitudePlugin.getOriginSkillId())
            var originSkillElement = SkillWidgetElement(originSkill!!.id, aptitudePlugin.id, true, false, true, originSkill!!.iconPath, "leadership1", aptitudePlugin.getColor(), inner, 72f, 72f)
            inner.addTooltipTo(SCSkillTooltipCreator(data, originSkill.getPlugin(), aptitudePlugin, 0, false), originSkillElement.elementPanel, TooltipMakerAPI.TooltipLocation.BELOW)
            //originSkillElement.elementPanel.position.rightOfMid(officerPickerElement.elementPanel, 20f)
            originSkillElement.elementPanel.position.rightOfMid(background.elementPanel, 20f)

            originSkillElement.onClick {
                Global.getSoundPlayer().playUISound("ui_button_pressed", 1f, 1f)
                selectedOfficer = officer
            }


            var originGap = SkillGapElement(aptitudePlugin.getColor(), inner)
            originGap.elementPanel.position.rightOfTop(originSkillElement.elementPanel, 0f)
            originGap.renderArrow = true

            var previousSections = ArrayList<SCAptitudeSection>()
            var skillElements = ArrayList<SkillWidgetElement>()
            var previous: CustomPanelAPI = originGap.elementPanel
            for (section in sections) {

                var isLastSection = sections.last() == section
                var canOnlyChooseOne = !section.canChooseMultiple

                var firstSkillThisSection: SkillWidgetElement? = null
                var usedWidth = 0f

                section.previousUISections.addAll(previousSections)
                previousSections.add(section)

                var skills = section.getSkills()
                for (skill in skills) {
                    var skillSpec = SCSpecStore.getSkillSpec(skill)
                    var skillPlugin = skillSpec!!.getPlugin()

                    var isFirst = skills.first() == skill
                    var isLast = skills.last() == skill

                    var preacquired = false
                    var activated = false
                    if (officer.activeSkillIDs.contains(skill)) {
                        preacquired = true
                        activated = true
                    }

                    var skillElement = SkillWidgetElement(skill, aptitudePlugin.id, activated, false, preacquired, skillPlugin!!.getIconPath(), section.soundId, aptitudePlugin.getColor(), inner, 72f, 72f)
                    skillElement.onClick {
                        Global.getSoundPlayer().playUISound("ui_button_pressed", 1f, 1f)
                        selectedOfficer = officer
                    }
                    skillElements.add(skillElement)
                    section.activeSkillsInUI.add(skillElement)
                    usedWidth += 72f

                    var tooltip = SCSkillTooltipCreator(data, skillPlugin, aptitudePlugin, section.requiredPreviousSkills, !section.canChooseMultiple)

                    if (section.requiredPreviousSkills != 0) {
                        tooltip.sectionMeetsRequirements = false
                    }

                    inner.addTooltipTo(tooltip, skillElement.elementPanel, TooltipMakerAPI.TooltipLocation.BELOW)
                    section.tooltips.add(tooltip)

                    if (firstSkillThisSection == null) {
                        firstSkillThisSection = skillElement
                    }

                    if (isFirst) {
                        skillElement.elementPanel.position.rightOfTop(previous, 0f)
                    } else {
                        skillElement.elementPanel.position.rightOfTop(previous, 3f)
                        usedWidth += 3f
                    }

                    if (!isLast) {
                        var seperator = SkillSeperatorElement(aptitudePlugin.getColor(), inner)
                        seperator.elementPanel.position.rightOfTop(skillElement.elementPanel, 3f)
                        previous = seperator.elementPanel
                        usedWidth += 3f
                    }
                    else if (!isLastSection) {
                        var gap = SkillGapElement(aptitudePlugin.getColor(), inner)
                        gap.elementPanel.position.rightOfTop(skillElement.elementPanel, 0f)
                        previous = gap.elementPanel

                        var nextIndex = sections.indexOf(section) + 1
                        var nextSection = sections.getOrNull(nextIndex)
                        if (nextSection != null) {
                            nextSection.uiGap = gap
                        }

                    }

                    if (canOnlyChooseOne) {
                        var underline = SkillUnderlineElement(aptitudePlugin.getColor(), 2f, inner, usedWidth)
                        underline.position.belowLeft(firstSkillThisSection.elementPanel, 2f)
                    }


                }
            }

            if (categories.isNotEmpty()) {

                var anchor = inner.addLunaElement(20f, 20f).apply {
                    renderBackground = false
                    renderBorder = false
                }
                anchor.elementPanel.position.belowLeft(officerPickerElement.elementPanel, 8f)

                var categoryNames = ArrayList<String>()
                var categoryColors = ArrayList<Color>()
                var categoryText = ""

                for (category in categories) {
                    categoryNames.add(category.name)
                    categoryColors.add(Misc.getTextColor())

                    categoryText += "${category.name}, "
                }

                categoryText = categoryText.trim()
                categoryText = categoryText.trim { it == ',' }

                var extraS = "y"
                if (categories.size >= 2) extraS = "ies"

                var label = inner.addPara("类别：{$categoryText", 0f, Misc.getGrayColor(), Misc.getHighlightColor())
                //label.position.rightOfMid(categoryHelp.elementPanel, 5f)
                label.position.rightOfMid(anchor.elementPanel, -16f)

                label.setHighlight("类别：{",*categoryNames.toTypedArray())
                label.setHighlightColors(aptitudePlugin.color, *categoryColors.toTypedArray())

                var length = label.computeTextWidth(label.text)

                var categoryBackground = inner.addLunaElement(length + 8 + 4, 24f).apply {
                    enableTransparency = true
                    renderBackground = false
                    renderBorder = false
                    /*  backgroundAlpha = 0.025f
                      borderAlpha = 0.4f
                      backgroundColor = aptitudePlugin.color
                      borderColor = aptitudePlugin.color*/
                }

                categoryBackground.elementPanel.position.rightOfMid(anchor.elementPanel, -16f - 4)

                categoryBackground.onClick {
                    Global.getSoundPlayer().playUISound("ui_button_pressed", 1f, 1f)
                    selectedOfficer = officer
                }

                inner.addTooltip(categoryBackground.elementPanel, TooltipMakerAPI.TooltipLocation.BELOW, 250f) { tooltip ->
                    tooltip.addPara("某些天赋属于特定的{类别}。你无法同时指派多名{属于同一类别}的军官。", 0f,
                        Misc.getTextColor(), Misc.getHighlightColor(), "类别", "属于同一类别")
                }

                /*     var categoryHelp = HelpIconElement(Misc.getBasePlayerColor(), inner, 20f, 20f)
                     categoryHelp.elementPanel.position.rightOfMid(anchor.elementPanel, length - 20f + 4)*/
            }

            //Para
            var paraAnchorElement = inner.addLunaElement(0f, 0f)
            paraAnchorElement.position.aboveLeft(originSkillElement.elementPanel, 6f)

            var officerPara = inner.addPara("${officer.person.nameString} - 1 技能点", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "1")
            officerPara.position.rightOfBottom(paraAnchorElement.elementPanel, 0f)





            //Non-Recommmended Header
            if (recommended.contains(officer.aptitudeId)) {
                recommended.remove(officer.aptitudeId)
                if (recommended.isEmpty()) {
                    //Recommended Header
                    scrollerElement.addSpacer(10f)
                    var nonRecommendedHeader = scrollerElement.addSectionHeading("高级 & 专用军官", Alignment.MID, 0f)
                    nonRecommendedHeader.position.setXAlignOffset(10f)
                    nonRecommendedHeader.position.setSize(nonRecommendedHeader.position.width - 25, nonRecommendedHeader.position.height)
                }
            }

        }

        scrollerElement.addSpacer(10f)

        scrollerPanel.addUIElement(scrollerElement)


        var buttonPanel = panel.createCustomPanel(width, heightCap, null)
        panel.addComponent(buttonPanel)
        buttonPanel.position.belowLeft(scrollerPanel, 0f)

        var buttonElement = buttonPanel.createUIElement(width, height, false)
        buttonElement.position.inTL(0f, 0f)
        buttonPanel.addUIElement(buttonElement)
        buttonElement.addPara("", 0f)

        var confirmButton = ConfirmCancelButton(Misc.getGrayColor(), buttonElement, 120f, 35f).apply {
            addText("确定")
            centerText()
            blink = false
            position.inTR(150f + 35, 14f)
        }

        confirmButton.advance {
            if (selectedOfficer != null) {
                var plugin = SCSpecStore.getAptitudeSpec(selectedOfficer!!.aptitudeId)!!.getPlugin()
                confirmButton.color = plugin.getColor()
                confirmButton.blink = true
            }
        }

        confirmButton.onClick {

            if (selectedOfficer == null) {
                Global.getSoundPlayer().playUISound("ui_button_disabled_pressed", 1f, 1f)
                return@onClick
            }

            confirmButton.playSound(Sounds.STORY_POINT_SPEND, 1f, 1f)
            callbacks!!.dismissDialog()
            plugin.chooseOfficer(selectedOfficer!!)

        }

        var cancelButton = ConfirmCancelButton(Misc.getBasePlayerColor(), buttonElement, 120f, 35f).apply {
            addText("取消")
            centerText()
            blink = false
            position.rightOfTop(confirmButton.elementPanel, 10f)
        }

        cancelButton.onClick {
            cancelButton.playClickSound()
            callbacks!!.dismissDialog()
        }

        var helpIcon = HelpIconElement(Misc.getBasePlayerColor(), buttonElement, 35f, 35f)
        helpIcon.elementPanel.position.rightOfMid(cancelButton.elementPanel, 6f)

        buttonElement.addTooltip(helpIcon.elementPanel, TooltipMakerAPI.TooltipLocation.ABOVE, 400f) { tooltip ->
		tooltip.addPara("执行军官}和通常的舰船指挥军官不同。他们专精于能够对整支舰队提供支持的特殊技能。同时只能指派 3 名执行军官。 \n\n" +
                    "你偶尔能在殖民地的{通讯目录}中找到待雇佣的执行军官。 他们也可能在探险时出现在被遗弃舰船上的{休眠舱}之中。 \n\n" +
                    "" +
                    "你无法同时指派多名{具有相同天赋的军官}。 " +
                    "此外，有些军官的天赋属于特定的{类别}。属于同一类别的军官，比如 \"后勤\"，也无法被同时指派。 ",
                0f, Misc.getTextColor(), Misc.getHighlightColor(), "执行军官", "通讯目录", "休眠舱",
                "具有相同天赋的军官", "类别", "后勤")
        }

    }

    override fun getCustomPanelPlugin(): CustomUIPanelPlugin? {
        return null
    }

    override fun getNoiseAlpha(): Float {
        return 0f
    }

    override fun advance(amount: Float) {

    }

    override fun reportDismissed(option: Int) {

    }


}