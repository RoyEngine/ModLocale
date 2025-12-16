package second_in_command.ui

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.characters.FullName
import com.fs.starfarer.api.characters.PersonAPI
import com.fs.starfarer.api.impl.campaign.ids.Sounds
import com.fs.starfarer.api.ui.CustomPanelAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.ui.UIPanelAPI
import com.fs.starfarer.api.util.Misc
import lunalib.lunaExtensions.addLunaElement
import lunalib.lunaExtensions.addLunaSpriteElement
import lunalib.lunaExtensions.addLunaTextfield
import lunalib.lunaUI.elements.LunaSpriteElement
import second_in_command.SCData
import second_in_command.misc.addNegativePara
import second_in_command.misc.addTooltip
import second_in_command.misc.getAndLoadSprite
import second_in_command.specs.SCAptitudeSection
import second_in_command.specs.SCCategorySpec
import second_in_command.specs.SCOfficer
import second_in_command.specs.SCSpecStore
import second_in_command.ui.elements.*
import second_in_command.ui.panels.BackgroundPanelPlugin
import second_in_command.ui.panels.ManagePanelPlugin
import second_in_command.ui.tooltips.OfficerTooltipCreator
import second_in_command.ui.tooltips.SCSkillTooltipCreator
import java.awt.Color

class SCOfficerPickerMenuPanel(var menu: SCSkillMenuPanel, var originalPickerElement: SCOfficerPickerElement, var subpanelParent: CustomPanelAPI, var slotId: Int, var data: SCData, var isAtColony: Boolean) {

    var activePanel: CustomPanelAPI? = null
    var activeElement: TooltipMakerAPI? = null

    var selectedOfficer: SCOfficer? = null

    var lastScroller = 0f

    companion object {
        fun openPortraitPicker(officer: PersonAPI, menu: SCSkillMenuPanel) {
            var plugin = BackgroundPanelPlugin(menu.panel)

            var width = 530f
            var height = 500f

            var portraitPanel = menu.panel.createCustomPanel(width, height, plugin)
            plugin.panel = portraitPanel
            menu.panel.addComponent(portraitPanel)
            portraitPanel.position.inMid()

            var element = portraitPanel!!.createUIElement(width, height, true)
            element.position.inTL(0f, 0f)

            var lastElement: UIPanelAPI? = null
            var lastRowElement: UIPanelAPI? = null
            var elementPerRow = 5
            var currentCount = 0
            var size = 96f

            var portraits = ArrayList<String>()
            portraits += Global.getSector().playerFaction.factionSpec.getAllPortraits(FullName.Gender.MALE)
            portraits += Global.getSector().playerFaction.factionSpec.getAllPortraits(FullName.Gender.FEMALE)
            portraits = portraits.distinct() as ArrayList<String>

            for (portrait in portraits) {

                var luna = element.addLunaSpriteElement(portrait, LunaSpriteElement.ScalingTypes.STRETCH_SPRITE, size, 0f).apply {
                    enableTransparency = true
                    width = 0f
                    height = 0f
                    getSprite().alphaMult = 0.6f

                    advance {
                        if (isHovering) {

                            getSprite().alphaMult = 1f
                        }
                        else {

                            getSprite().alphaMult = 0.7f
                        }
                    }

                    onClick {
                        plugin.close()
                        officer.portraitSprite = portrait
                        playClickSound()
                    }

                    onHoverEnter {
                        playScrollSound()
                    }
                }

                luna.position.setSize(size, size)
                luna.getSprite().setSize(size, size)

                if (currentCount == 0) {
                    element.addSpacer(size + 10f)
                    if (lastRowElement != null) {
                        luna.elementPanel.position.belowLeft(lastRowElement, 10f)
                    }
                    lastRowElement = luna.elementPanel
                }
                else {
                    luna.elementPanel.position.rightOfMid(lastElement!!, 10f)
                }

                currentCount++

                if (currentCount == elementPerRow) {
                    currentCount = 0
                }

                lastElement = luna.elementPanel
            }

            portraitPanel.addUIElement(element)

        }
    }

    fun init() {
        recreatePanel()

    }

    fun recreatePanel() {

        if (activePanel != null) {
            if (activeElement != null) {
                lastScroller = activeElement!!.externalScroller.yOffset
            }

            menu.panel.removeComponent(activePanel)
        }

        var plugin = BackgroundPanelPlugin(menu.panel)

        var width = menu.width - 25
        var height = menu.height - 25

        var heightCap = 70f

        var popupPanel = menu.panel.createCustomPanel(width, height, plugin)
        plugin.panel = popupPanel
        menu.panel.addComponent(popupPanel)
        popupPanel.position.inMid()

        activePanel = popupPanel

        var scrollerPanel = popupPanel.createCustomPanel(width, height - heightCap, null)
        popupPanel.addComponent(scrollerPanel)
        scrollerPanel.position.inTL(0f, 0f)
        var scrollerElement = scrollerPanel.createUIElement(width, height - heightCap, true)

        activeElement = scrollerElement

        //var officers = data.getOfficersInFleet().sortedByDescending { it.isAssigned() }
        var officers = data.getOfficersInFleet().sortedWith(compareBy({ !it.isAssigned() }, { it.getAptitudeSpec().order }))
        var activeOfficers = data.getAssignedOfficers()

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



            officerElement.onClick { selectOfficer(officer) }


            var inner = officerElement.innerElement
            inner.addSpacer(24f)

            var officerPickerElement = SCOfficerPickerElement(officer.person, aptitudePlugin.getColor(), inner, 96f, 96f)
            officerPickerElement.onClick { selectOfficer(officer) }

            var paraElement = inner.addLunaElement(100f, 20f).apply {
                renderBorder = false
                renderBackground = false
            }
            paraElement.elementPanel.position.aboveMid(officerPickerElement.elementPanel, 0f)

            paraElement.innerElement.setParaFont("graphics/fonts/victor14.fnt")
            var aptitudePara = paraElement.innerElement.addPara(aptitudePlugin.getName(), 0f, aptitudePlugin.getColor(), aptitudePlugin.getColor())
            aptitudePara.position.inTL(paraElement.width / 2 - aptitudePara.computeTextWidth(aptitudePara.text) / 2 - 1, paraElement.height  -aptitudePara.computeTextHeight(aptitudePara.text)-5)


           /* officerPickerElement.innerElement.setParaFont("graphics/fonts/victor14.fnt")
            var aptitudePara = officerPickerElement.innerElement.addPara(aptitudePlugin.getName(), 0f, aptitudePlugin.getColor(), aptitudePlugin.getColor())
            aptitudePara.position.inTL(officerPickerElement.width / 2 - aptitudePara.computeTextWidth(aptitudePara.text) / 2 - 1, -aptitudePara.computeTextHeight(aptitudePara.text)-5)

            */

            scrollerElement.addTooltipTo(OfficerTooltipCreator(officer, isAtColony, true), officerPickerElement.elementPanel, TooltipMakerAPI.TooltipLocation.RIGHT)

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

            originSkillElement.onClick { selectOfficer(officer) }


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
                    skillElement.onClick { selectOfficer(officer) }
                    skillElements.add(skillElement)
                    section.activeSkillsInUI.add(skillElement)
                    usedWidth += 72f

                    var tooltip = SCSkillTooltipCreator(data, skillPlugin, aptitudePlugin, section.requiredPreviousSkills, !section.canChooseMultiple)
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

            //Category Section

            if (categories.isNotEmpty()) {
               /* var categoryHelp = HelpIconElement(aptitudePlugin.color, inner, 24f, 24f)
                categoryHelp.elementPanel.position.belowLeft(officerPickerElement.elementPanel, 8f)*/

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

                categoryBackground.onClick { selectOfficer(officer) }

                inner.addTooltip(categoryBackground.elementPanel, TooltipMakerAPI.TooltipLocation.BELOW, 250f) { tooltip ->
				tooltip.addPara("某些天赋属于特定的{类别}。你无法同时指派多名{属于同一类别的军官}。", 0f,
                        Misc.getTextColor(), Misc.getHighlightColor(), "类别", "属于同一类别的军官")
                }

           /*     var categoryHelp = HelpIconElement(Misc.getBasePlayerColor(), inner, 20f, 20f)
                categoryHelp.elementPanel.position.rightOfMid(anchor.elementPanel, length - 20f + 4)*/
            }





            //Top Para
            var paraAnchorElement = inner.addLunaElement(0f, 0f)
            paraAnchorElement.position.aboveLeft(originSkillElement.elementPanel, 6f)

            var spRemaining = menu.calculateRemainingSP(officer, skillElements)
            var spHighlight = Misc.getHighlightColor()
            if (spRemaining <= 0) spHighlight = Misc.getGrayColor()

            var officerParaTextExtra = ""
            var minusText = ""

            if (officerAlreadySlotted(officer)) officerParaTextExtra = "这名军官已经被指派。"
            else if (doesOffficerMatchExistingAptitude(officer)) officerParaTextExtra = "无法同时指派多名具有相同天赋的军官。"
            else if (doesOffficerMatchCategory(officer)) officerParaTextExtra = "无法同时指派多名属于同一类别的军官。"

            if (officerParaTextExtra != "") minusText = "-"

            var officerPara = inner.addPara("${officer.person.nameString} - $spRemaining 技能点 $minusText $officerParaTextExtra", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "$spRemaining")
            officerPara.position.rightOfBottom(paraAnchorElement.elementPanel, 0f)

            officerPara.setHighlight("$spRemaining", officerParaTextExtra)
            officerPara.setHighlightColors(spHighlight, Misc.getNegativeHighlightColor())

            calculateSectionRequirements(officer, sections, skillElements)


        }

        scrollerElement.addSpacer(10f)

        scrollerPanel.addUIElement(scrollerElement)

        var buttonPanel = popupPanel.createCustomPanel(width, heightCap, null)
        popupPanel.addComponent(buttonPanel)
        buttonPanel.position.belowLeft(scrollerPanel, 0f)

        var buttonElement = buttonPanel.createUIElement(width, height, false)
        buttonElement.position.inTL(0f, 0f)
        buttonPanel.addUIElement(buttonElement)
        buttonElement.addPara("", 0f)

        //Confirm
        var confirmButton = ConfirmCancelButton(Misc.getGrayColor(), buttonElement, 120f, 35f).apply {
            addText("确认")
            centerText()
            blink = false
            position.inTR(150f+130+35+2, 14f)
        }

        confirmButton.advance {
            if (selectedOfficer != null) {

                if (officerAlreadySlotted(selectedOfficer!!) || doesOffficerMatchExistingAptitude(selectedOfficer!!) || doesOffficerMatchCategory(selectedOfficer!!)) {

                    confirmButton.color = Misc.getGrayColor()
                    confirmButton.blink = false

                    return@advance
                }

                var plugin = SCSpecStore.getAptitudeSpec(selectedOfficer!!.aptitudeId)!!.getPlugin()
                confirmButton.color = plugin.getColor()
                confirmButton.blink = true
            }
        }

        confirmButton.onClick {

            if (selectedOfficer == null || (officerAlreadySlotted(selectedOfficer!!) || doesOffficerMatchExistingAptitude(selectedOfficer!!) || doesOffficerMatchCategory(selectedOfficer!!))) {
                Global.getSoundPlayer().playUISound("ui_button_disabled_pressed", 1f, 1f)
                return@onClick
            }

            confirmButton.playClickSound()
            menu.panel.removeComponent(popupPanel)

            menu.checkToApplyCRPenalty()

            var previousOfficerInSlot = data.getOfficerInSlot(slotId)
            data.setOfficerInSlot(slotId, selectedOfficer!!)

            menu.recreateAptitudeRow(subpanelParent, data.getOfficerInSlot(slotId), slotId)
        }

        //Manage
        var manageButton = ConfirmCancelButton(Misc.getGrayColor(), buttonElement, 120f, 35f).apply {

            addText("管理")
            centerText()
            blink = false
            position.rightOfTop(confirmButton.elementPanel, 10f)
        }

        manageButton.advance {
            if (selectedOfficer != null) {

                var aptitude = selectedOfficer!!.getAptitudeSpec()
                var plugin = aptitude.getPlugin()
                if (aptitude.tags.contains("unmanageable")) {
                    manageButton.color = Misc.getGrayColor()
                    manageButton.blink = false
                } else {
                    var plugin = SCSpecStore.getAptitudeSpec(selectedOfficer!!.aptitudeId)!!.getPlugin()
                    manageButton.color = plugin.getColor()
                    manageButton.blink = true
                }

            }
        }

        manageButton.onClick {

            if (selectedOfficer == null) {
                Global.getSoundPlayer().playUISound("ui_button_disabled_pressed", 1f, 1f)
                return@onClick
            }

            var aptitude = selectedOfficer!!.getAptitudeSpec()
            if (aptitude.tags.contains("unmanageable")) {
                Global.getSoundPlayer().playUISound("ui_button_disabled_pressed", 1f, 1f)
                return@onClick
            }

            manageButton.playClickSound()
            var plugin = openOfficerManagementPanel(popupPanel, selectedOfficer!!)
            plugin.onClose = {
                if (selectedOfficer != null) {
                    var slot = data.getOfficersAssignedSlot(selectedOfficer!!)
                    if (slot == slotId) {
                        menu.recreateAptitudeRow(subpanelParent, selectedOfficer, slot)
                    }
                    /*else if (slot != null) {
                        menu.recreateAptitudeRow(subpanelParent, selectedOfficer, slot)
                    }*/
                } /*else {
                    //Clear the slot if the officer was dismissed
                    menu.recreateAptitudeRow(subpanelParent, null, slotId)
                }*/

                //Clear Slots of dismissed officers
                for (i in 0 ..2) {
                    if (!data.getOfficersInFleet().contains(data.getOfficerInSlot(i))) {
                        menu.recreateAptitudeRow(menu.rowParents.get(i)!!, null, i)
                    }
                }

            }

        }

        buttonElement.addTooltip(manageButton.elementPanel, TooltipMakerAPI.TooltipLocation.BELOW, 250f) { tooltip ->
            tooltip.addPara("修改一名军官的{姓名}或将其{解雇}，又或是修改其{头像}。 ", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "姓名", "解雇", "头像")

            if (selectedOfficer != null) {
                var aptitude = selectedOfficer!!.getAptitudeSpec()
                if (aptitude.tags.contains("unmanageable")) {
                    tooltip.addSpacer(10f)
                    tooltip.addNegativePara("This officer can not be managed")
                }
            }

        }

        //Cancel
        var cancelButton = ConfirmCancelButton(Misc.getBasePlayerColor(), buttonElement, 120f, 35f).apply {
            addText("取消")
            centerText()
            blink = false
            //position.rightOfTop(confirmButton.elementPanel, 10f)
            position.rightOfTop(manageButton.elementPanel, 10f)
        }

        cancelButton.onClick {
            cancelButton.playClickSound()
            menu.panel.removeComponent(popupPanel)
        }


        scrollerElement.externalScroller.yOffset = lastScroller


         var helpIcon = HelpIconElement(Misc.getBasePlayerColor(), buttonElement, 35f, 35f)
         helpIcon.elementPanel.position.rightOfMid(cancelButton.elementPanel, 6f)

            buttonElement.addTooltip(helpIcon.elementPanel, TooltipMakerAPI.TooltipLocation.ABOVE, 400f) { tooltip ->
                tooltip.addPara("这个界面可以用于{指派}、{解雇}或{重命名}你麾下的{执行军官}。 \n\n" +
                        "" +
                        "执行军官和通常的舰船指挥军官不同。他们专精于能够对整支舰队提供支持的特殊技能。同时只能指派 3 名执行军官。 \n" + "\n" +
                        "你偶尔能在殖民地的{通讯目录}中找到待雇佣的执行军官。 他们也可能在探险时出现在被遗弃舰船上的{休眠舱}之中。 \n\n" +
                        "" +
                        "你无法同时指派多名{具有相同天赋的军官}。 " +
                        "此外，有些军官的天赋属于特定的{类别}。天赋异禀为同一类别的军官，比如 \"后勤\"，也无法被同时指派。 ",
                    0f, Misc.getTextColor(), Misc.getHighlightColor(), "指派", "解雇", "重命名", "执行军官", "通讯目录", "休眠舱",
                    "具有相同天赋的军官", "类别", "后勤")
            }
    }

    fun openOfficerManagementPanel(popupPanel: CustomPanelAPI, officer: SCOfficer) : ManagePanelPlugin {
        var plugin = ManagePanelPlugin(popupPanel, this)

        var width = 316f
        var height = 170f

        var managementPanel = menu.panel.createCustomPanel(width, height, plugin)
        plugin.panel = managementPanel
        popupPanel.addComponent(managementPanel)
        managementPanel.position.inMid()

        var element = managementPanel.createUIElement(width, height, false)
        managementPanel.addUIElement(element)


        var portraitElement = element.addLunaElement(128f, 128f)
        portraitElement.position.inTL(20f, 20f)

        portraitElement.render {
            var path = officer.person.portraitSprite
            var sprite = Global.getSettings().getAndLoadSprite(path)

            sprite.setSize(128f, 128f)
            sprite.alphaMult = 1f
            sprite.setNormalBlend()
            sprite.render(portraitElement.elementPanel.position.x, portraitElement.elementPanel.position.y)

            if (portraitElement.isHovering) {
                sprite.setAdditiveBlend()
                sprite.alphaMult = 0.3f
                sprite.render(portraitElement.elementPanel.position.x, portraitElement.elementPanel.position.y)
            }
        }

        portraitElement.onHoverEnter {
            portraitElement.playScrollSound()
        }

        portraitElement.onClick {
            portraitElement.playClickSound()
            openPortraitPicker(officer.person, menu)
        }

        element.addTooltip(portraitElement.elementPanel, TooltipMakerAPI.TooltipLocation.BELOW, 350f ) {
            it.addPara("点击以修改军官头像。你可以从任何 开始新游戏 时玩家的可选头像当中选择。", 0f)
        }

        var nameElement = element.addLunaTextfield(officer.person.nameString, false, 128f, 30f).apply {
            enableTransparency = true
        }
        //nameElement.position.inTMid(20f)
        nameElement.position.rightOfTop(portraitElement.elementPanel, 20f)

        nameElement.advance {
            var officerName = officer.person.nameString
            if (officerName != nameElement.getText()) {
                var space = nameElement.getText().indexOf(" ")

                if (space == -1) {
                    officer.person.name.first = nameElement.getText()
                } else {
                    var first = nameElement.getText().substring(0, space)
                    var last = nameElement.getText().substring(space+1, nameElement.getText().length)
                    var fullname = "$first $last"

                    if (last == "") {
                        fullname = first
                    }

                    officer.person.name.first = first
                    officer.person.name.last = last
                    //nameElement.changePara(fullname)

                }
            }
        }

        var dismissButton = ConfirmCancelButton(Misc.getNegativeHighlightColor(), element, 128f, 30f).apply {
            addText("解雇")
            centerText()
            blink = false
            position.belowLeft(nameElement.elementPanel, 20f)
        }

        dismissButton.onClick {
            dismissButton.playClickSound()
            if (it.isDoubleClick && it.isLMBDownEvent) {
                selectedOfficer = null
                dismissButton.playSound(Sounds.STORY_POINT_SPEND, 1f, 1f)
                data.removeOfficerFromFleet(officer)
                plugin.close()
            }
        }

        element.addTooltip(dismissButton.elementPanel, TooltipMakerAPI.TooltipLocation.BELOW, 300f) { tooltip ->
            tooltip.addPara("快速连续点击此按钮{两次}，以{永久解雇}这名军官。被解雇的军官将从你的舰队中彻底消失。",
                0f, Misc.getTextColor(), Misc.getHighlightColor(), "两次", "永久解雇")
        }

        var closeButton = ConfirmCancelButton(Misc.getGrayColor(), element, 128f, 30f).apply {
            addText("关闭")
            centerText()
            blink = false
            position.belowLeft(dismissButton.elementPanel, 20f)
        }

        closeButton.onClick {
            closeButton.playClickSound()
            plugin.close()
        }

        return plugin

    }



    fun selectOfficer(officer: SCOfficer) {

        /*if (officerAlreadySlotted(officer) || doesOffficerMatchExistingAptitude(officer) || doesOffficerMatchCategory(officer)) {
            Global.getSoundPlayer().playUISound("ui_button_disabled_pressed", 1f, 1f)
            return
        }*/

        Global.getSoundPlayer().playUISound("ui_button_pressed", 1f, 1f)
        selectedOfficer = officer
    }


    fun doesOffficerMatchExistingAptitude(officer: SCOfficer) : Boolean {

        for (active in data.getAssignedOfficers()) {
            if (active == null) continue
            if (active.person == originalPickerElement.officer) continue
            if (active.aptitudeId == officer.aptitudeId) return true
        }

        return false
    }



    fun doesOffficerMatchCategory(officer: SCOfficer) : Boolean {
        var list = mutableListOf<SCCategorySpec>()
        var categories = officer.getAptitudePlugin().categories
        for (active in data.getAssignedOfficers()) {
            if (active == null) continue
            if (active.person == originalPickerElement.officer) continue

            var othersCategories = active.getAptitudePlugin().categories

            if (othersCategories.any { categories.contains(it) }) {
                return true
            }
        }

        return false
    }

    fun officerAlreadySlotted(officer: SCOfficer) : Boolean {
        return data.getAssignedOfficers().contains(officer)
    }

    fun getActiveSkillCount(sections: ArrayList<SCAptitudeSection>) : Int {
        return sections.sumOf { it.activeSkillsInUI.count { it.activated } }
    }

    fun calculateSectionRequirements(officer: SCOfficer, sections: MutableList<SCAptitudeSection>, skillElements: ArrayList<SkillWidgetElement>) {
        for (section in sections) {

            var count = getActiveSkillCount(section.previousUISections)

            section.uiGap?.renderArrow = section.requiredPreviousSkills <= count
            section.tooltips.forEach { it.sectionMeetsRequirements = section.requiredPreviousSkills <= count }

        }
    }

}